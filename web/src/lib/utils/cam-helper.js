import {
    Html5Qrcode,
    Html5QrcodeSupportedFormats
} from 'html5-qrcode';

import {
    scan_pin_request_done,
    set_bcur1_fragments,
} from './jade-proto.js';

// functioning variable
var html5qr = null;
var running = false;
//var bcur1_fragments;
var seenFrags = null;
var expectedFrags = 0;

// Progress Bar
var camProgressBarState = null;

// button states
var pinState = null;

// Zoom track
var currentZoom = 1.0;
var minZoom = 1.0;
var maxZoom = 4.0;
var activeCapabilities = {}
var initialTouchDistance = 0;

// Alerts
var alertState = null;
var zoomAlertState = null;

// Pin Request State
var pinRequestState = null;

/**
 * Registers the Alert State for the Notification values
 * (Reactive)
 * @param stateObj contains the alertstate for Notifications
 *      kind: "error" | "info" | "info-square" | "success" | "warning" | "warning-alt",
 *      title: string,
 *      subtitle: string,
 *      open: boolean
 */
export function registerAlertNotification(stateObj) {
    alertState = stateObj;
}

/**
 * Registers the Zoom Alert State for the Notification Values
 * (Reactive)
 * @param stateObj contains the zoomalertstate for Notifications
 *      kind: "error" | "info" | "info-square" | "success" | "warning" | "warning-alt",
 *      title: string,
 *      subtitle: string,
 *      open: boolean
 */
export function registerZoomAlertNotification(stateObj) {
    zoomAlertState = stateObj;
}

/**
 * Registers the Progress Bar
 * @param {Object} stateObj 
 * Progress Bar include {
 *      active: boolean,
 *      value: number,
 *      max: number,
 *      statusText: string
 * }
 */
export function registerProgressBarState(stateObj) {
    camProgressBarState = stateObj;
}

/**
 * Register Pin State
 * Pin State Object includes {
 * 
 *      buttonScanStartDisabled: boolean,
 *      buttonScanStopDisabled: boolean,
 *      buttonReplyDisabled: boolean,
 *      qr_pin_request: string,
 *      qr_pin_reply: string,
 *      replyFunction: string,
 *      isReplyGenerating: boolean 
 * }
 * @param {Object} stateObj 
 */
export function registerPinState(stateObj) {
    pinState = stateObj;
}

/**
 * Show Alert
 * @param {"error" | "info" | "info-square" | "success" | "warning" | "warning-alt"} kind 
 * @param {string} title 
 * @param {string} subtitle 
 * @returns 
 */
function showAlert(kind, title, subtitle) {
    if (!alertState ) {
        return;
    }

    alertState.kind = kind;
    alertState.title = title;
    alertState.subtitle = subtitle;
    alertState.open = true;
}

/**
 * Show Zoom Alert
 * @param {"error" | "info" | "info-square" | "success" | "warning" | "warning-alt"} kind 
 * @param {string} title 
 * @param {string} subtitle 
 * @returns 
 */
function showZoomAlert(kind, title, subtitle) {
    if (!zoomAlertState) {
        return;
    }

    zoomAlertState.kind = kind;
    zoomAlertState.title = title;
    zoomAlertState.subtitle = subtitle;
    zoomAlertState.open = true;
}

/**
 * Clears Alert Notification
 * Turns off and sets state to default
 * @returns 
 */
function clearAlert() {
    if (!alert) {
        return;
    }
    alertState.kind = "info";
    alertState.title = "";
    alertState.subtitle = "";
    alertState.open = false;
}

/**
 * Clears Zoom Alert Notification
 * Turns off and sets state to default
 * @returns 
 */
function clearZoomAlert() {
    if (!zoomAlertState ) {
        return;
    }
    zoomAlertState.kind = "info";
    zoomAlertState.title = "";
    zoomAlertState.subtitle = "";
    zoomAlertState.open = false;
}

/**
 * Sets the Progress Bar values
 * (Reactive)
 * @param {boolean} active 
 * @param {number} value 
 * @param {number} max 
 * @param {string} statusText 
 * @returns 
 */
function setProgress(active, value = 0, max = 1, statusText = "") {
    if (!camProgressBarState) {
        return;
    }
    
    camProgressBarState.active = active;
    if (active) {
        camProgressBarState.value = value;
        camProgressBarState.max = max;
        camProgressBarState.statusText = statusText;
    }
}

function resetFragments() {
    seenFrags = null;
    expectedFrags = 0;
    set_bcur1_fragments(null);
}

function onDecoded(result) {
    var parts = String(result).split("/");

    if (parts[0].toLocaleLowerCase() !== "ur:jade-pin") {
        showAlert(
            "warning",
            "Not a Jade PIN QR Code.",
            "Make sure using Jade QR Code"
        );
        return;
    }

    if (parts.length == 3) {
        var seqParts = parts[1].split("-");
        var seq = parseInt(seqParts[0], 10);
        var total = parseInt(seqParts[1], 10);

        if (seenFrags === null) {
            seenFrags = new Array(total).fill(null);
            expectedFrags = total;
        }

        // skip if not within seq
        if (seq > total)
        {
            return;
        }
        // skip if flag is duplicate
        if (seenFrags[seq - 1] !== null)
        {
            return;
        }

        seenFrags[seq - 1] = result;

        var have = seenFrags.filter(function (f) { return f !== null; }).length;
        
        setProgress(
            true,
            have,
            total,
            "Captured " + have + " of " + total + " QR frames."
        );

        if (have === total) {
            finish(seenFrags);
        }
    } else if (parts.length === 2) {
      // Single-part payload.
      finish([result]);
    }
}

function finish(frags) {
    set_bcur1_fragments(frags);
    stopCameraScanning();
    setProgress(false);
    showAlert(
        "success",
        "PIN Request Captured.",
        "Continue to next step."
    );

    try {
        const { data, replyPinFunc } = scan_pin_request_done();
        
        pinState.buttonReplyDisabled = false;
        pinState.replyFunction = replyPinFunc;
        pinState.qr_pin_request = data;

    } catch (e) {
      showAlert(
        "error",
        "Could not decode the captured data.",
        e.message
        );
    }
  }

function preflight() {
    if (!window.isSecureContext) {
        showAlert(
            "error",
            "Security Error",
            "Camera requires a secure HTTPS context."
        );
        return false;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia)  {
        showAlert(
            "error",
            "Not Found Error",
            "navigator.mediaDevices.getUserMedia is not supported by this browser."
        );
        return false;
    }

    return true;
}

function getElementFrom(element) {
    return typeof element === 'string' ? document.getElementById(element) ||
        document.querySelector(element) : element;
}

function NotifyCameraError(err) {
    var name = (err && err.name) || "";
    var msg = (err && err.message) || String(err);

    if (name === "NotAllowedError" || name === "SecurityError") {
        showAlert(
            "error",
            "Camera Permission Denied.",
            "Grant camera access and try again."
        );
    } else if (name === "NotFoundError" || name === "DevicesNotFoundError") {
      showAlert(
        "error",
        "No Camera was Detected.",
        "No video input device is visible to this."
      );
    } else if (name === "NotReadableError" || name === "TrackStartError") {
      showAlert(
        "error",
        "Camera is Used By Another.",
        "Another program is holding the device."
        );
    } else if (name === "OverconstrainedError") {
      showAlert(
        "error",
        "Camera Doesn't Support Mode.",
        "Pick a different device from the dropdown"
        );
    } else {
      showAlert(
        "error",
        "Could Not Start the Camera.",
        ""
      );
    }
}

// ... existing code ...

export function listCameras(buttonScanElement="btn_scan") {
  if (!preflight()) return Promise.resolve([]);
  
  return Html5Qrcode.getCameras().then(function (devices) {
    if (!devices || devices.length === 0) {
        showAlert(
            "warning",
            "No Camera Found",
            "Ensure you are on https and browser's camera permissions are set."
        );
      return [];
    }
    clearAlert();
    return devices;
  }).catch(function (err) {
    NotifyCameraError(err);
    return [];
  });
}

// ... existing code ...
export function startCameraScanning(camId) {
    
    if (!preflight()) return;

    if (running) return;

    resetFragments();
    clearAlert();
    clearZoomAlert();

    html5qr = new Html5Qrcode(
        "qrreader1",
        {
            formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
            verbose: true
        }
    );

    var config = { fps: 10, qrbox: {width: 260, height: 260 }};
    var source = camId ? camId : { facingMode: "environment" };

    html5qr.start(source, config, onDecoded, function () { /* per-frame miss */ })
        .then(function () {
            running = true;

            if (pinState) {
                pinState.buttonScanStartDisabled = true;
                pinState.buttonScanStopDisabled = false;
            }

            setProgress(
                true,
                0,
                100,
                "Scanning... point the camera at the Jade QR Code."
            );

            // Zoom
            currentZoom = 1.0;
            // get capabilities
            try {
                activeCapabilities = html5qr.getRunningTrackCapabilities() || {};
            } catch (e) {
                activeCapabilities = {};
            }

            var hasZoom = false;
            var hasAutoFocus = false;

            // Get min and max
            if (activeCapabilities.zoom) {
                hasZoom = true;
                minZoom = activeCapabilities.zoom.min || 1.0;
                maxZoom = activeCapabilities.zoom.max || 5.0;
            } else {
                minZoom = 1.0;
                maxZoom = 4.0;
            }

            // Enable auto-focus if supported
            if (activeCapabilities.focusMode && activeCapabilities.focusMode.includes('continuous')) {
                hasAutoFocus = true;
                html5qr.applyVideoConstraints({
                    advanced: [{ focusMode: 'continuous' }]
                }).catch(function (err) {
                    console.warn("Could not set continous focus:", err);
                });
            }

            // set zoom gestures
            if (hasZoom)
                setupZoomGestures();

            if (!hasZoom && !hasAutoFocus)
            {
                showZoomAlert(
                    "warning",
                    "Zoom and Auto Focus",
                    "No zoom or auto focus capability for hardware/browser API"
                )
            }
            else if (!hasZoom)
            {
                showZoomAlert(
                    "warning",
                    "Zoom and Auto Focus",
                    "No zoom capability for hardware/browser API. Has auto focus capability."
                );
                
            }
            else if (!hasAutoFocus)
            {
                showZoomAlert(
                    "warning",
                    "Zoom and Auto Focus",
                    "No Auto Focus capability for hardware/browser API. Has zoom capability."
                );
            }
            else{
                showZoomAlert(
                    "success",
                    "Zoom and Auto Focus",
                    "Zoom and Auto Focus are capabily. Pinch and Zoom / Scroll Wheel gestures active."
                );
            }
        })
        .catch (function (err) {
            running = false;
            //TODO: EXPLAIN CAMERA ERR
        });
}

 function applyZoom(targetZoom) {
    currentZoom = Math.min(Math.max(targetZoom, minZoom), maxZoom);

    if (activeCapabilities.zoom) {
      // Only pass the advanced constraints block for running tracks
      var videoConstraints = {
        advanced: [{ zoom: currentZoom }]
      };

      html5qr.applyVideoConstraints(videoConstraints)
        .then(function () {
          console.log("Hardware zoom set to: ", currentZoom);
        })
        .catch (function (err) {
          console.warn("Hardware zoom adjustment rejected by browser:", err);
        });

    }
  }

  function handleWheelZoom(e) {
    e.preventDefault(); // Prevent entire page from scrolling down

      // Zoom in on scroll up, zoom out on scroll down
      var direction = e.deltaY < 0 ? 1 : -1;
      var step = 0.2;

      applyZoom(currentZoom + (direction * step));
  }

  function handleTouchStart(e) {
      if (e.touches.length === 2) {
        // User placed two fingers on camera surface; record base distance
        initialTouchDistance = getTouchDistance(e.touches[0], e.touches[1]);
      }
  }

  function handleTouchMove(e) {
      if (e.touches.length === 2 && initialTouchDistance > 0) {
        e.preventDefault(); // Stop mobile browser default page bouncing/scaling

        var currentDistance = getTouchDistance(e.touches[0], e.touches[1]);

        // Calculate pinch ratio change factor
        var scaleFactor = currentDistance / initialTouchDistance;

        // Adjust speed sensitivity factor
        var zoomChange = (scaleFactor - 1) * 1.2;

        applyZoom(currentZoom + zoomChange);

        // Reset point to keep gesture scaling proportional as fingers slide
        initialTouchDistance = currentDistance;
      }
    }

    function handleTouchEnd(e) {
      if (e.touches.length < 2) {
        initialTouchDistance = 0; // Reset tracking state when finger lifts
      }
    }


// --- DESKTOP SCROLLWHEEL & MOBILE PINCH GESTURES ---
  function setupZoomGestures() {
    var container = document.getElementById("qrreader1");
    if (!container) return;

    // 1. Desktop: Scroll wheel zoom listener
    container.addEventListener("wheel", handleWheelZoom, { passive: false });

    // 2. Mobile: Touch pinch-to-zoom listeners
    container.addEventListener("touchstart", handleTouchStart, { passive: true });
    container.addEventListener("touchmove", handleTouchMove, { passive: false });
    container.addEventListener("touchend", handleTouchEnd);
  }

  function cleanupZoomGestures() {
    var container = document.getElementById("qrreader1");
    if (!container) return;
    container.removeEventListener("wheel", handleWheelZoom);
    container.removeEventListener("touchstart", handleTouchStart);
    container.removeEventListener("touchmove", handleTouchMove);
    container.removeEventListener("touchend", handleTouchEnd);
  }

// Mathematical helper to calculate distance between two multi-touch points
  function getTouchDistance(touch1, touch2) {
    var dx = touch1.clientX - touch2.clientX;
    var dy = touch1.clientY - touch2.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  export function stopCameraScanning() {
    clearZoomAlert();
    cleanupZoomGestures();

    if (!html5qr || !running) return Promise.resolve();
        running = false;

    return html5qr.stop().then(function () {
      html5qr.clear();
      if (pinState) {
        pinState.buttonScanStartDisabled = false;
        pinState.buttonScanStopDisabled = true;
      }
      setProgress(false);
    }).catch(function () { /* already torn down */ });
  }