import XCTest
@testable import CortexShadowPointerNative

final class ShadowPointerNativeTests: XCTestCase {
    func testOverlaySpecIsTransparentNonActivatingAndPointerSafe() {
        let spec = NativeOverlayWindowSpec.shadowPointerDefault

        XCTAssertEqual(spec.policyRef, shadowPointerNativePolicyRef)
        XCTAssertEqual(spec.level, "floating")
        XCTAssertTrue(spec.styleMasks.contains("nonactivatingPanel"))
        XCTAssertTrue(spec.styleMasks.contains("borderless"))
        XCTAssertTrue(spec.collectionBehaviors.contains("canJoinAllSpaces"))
        XCTAssertTrue(spec.collectionBehaviors.contains("fullScreenAuxiliary"))
        XCTAssertFalse(spec.isOpaque)
        XCTAssertEqual(spec.backgroundColor, "clear")
        XCTAssertTrue(spec.ignoresMouseEventsByDefault)
        XCTAssertFalse(spec.canBecomeKey)
        XCTAssertFalse(spec.canBecomeMain)
    }

    func testPauseObservationBlocksObservationAndMemoryWrites() throws {
        let receipt = try ShadowPointerNativeControlBridge.apply(
            snapshot: .observingDefault,
            action: .pauseObservation,
            durationMinutes: 60
        )

        XCTAssertEqual(receipt.resultingSnapshot.state, .paused)
        XCTAssertFalse(receipt.observationActive)
        XCTAssertFalse(receipt.memoryWriteAllowed)
        XCTAssertTrue(receipt.auditRequired)
        XCTAssertEqual(receipt.auditAction, "pause_observation")
    }

    func testDeleteRecentRequiresConfirmationAndBlocksMemoryWrites() throws {
        XCTAssertThrowsError(
            try ShadowPointerNativeControlBridge.apply(
                snapshot: .observingDefault,
                action: .deleteRecent,
                deleteWindowMinutes: 10
            )
        )

        let receipt = try ShadowPointerNativeControlBridge.apply(
            snapshot: .observingDefault,
            action: .deleteRecent,
            deleteWindowMinutes: 10,
            userConfirmed: true
        )

        XCTAssertEqual(receipt.resultingSnapshot.state, .privateMasking)
        XCTAssertEqual(receipt.deletedWindowMinutes, 10)
        XCTAssertFalse(receipt.memoryWriteAllowed)
        XCTAssertEqual(receipt.auditAction, "delete_recent_observation")
    }

    func testIgnoreAppRequiresConfirmationAndRemovesAppFromSeeing() throws {
        XCTAssertThrowsError(
            try ShadowPointerNativeControlBridge.apply(
                snapshot: .observingDefault,
                action: .ignoreApp,
                appName: "Chrome"
            )
        )

        let receipt = try ShadowPointerNativeControlBridge.apply(
            snapshot: .observingDefault,
            action: .ignoreApp,
            appName: "Chrome",
            userConfirmed: true
        )

        XCTAssertEqual(receipt.resultingSnapshot.state, .privateMasking)
        XCTAssertFalse(receipt.resultingSnapshot.seeing.contains("Chrome"))
        XCTAssertTrue(receipt.resultingSnapshot.ignoring.contains("Chrome"))
        XCTAssertEqual(receipt.affectedApps, ["Chrome"])
        XCTAssertFalse(receipt.memoryWriteAllowed)
    }

    func testSmokeResultCoversControlAndDisplayOnlyBoundaries() throws {
        let result = try ShadowPointerNativeSmokeResult.run()

        XCTAssertTrue(result.passed)
        XCTAssertTrue(result.pauseBlocksMemory)
        XCTAssertTrue(result.deleteRecentBlocksMemory)
        XCTAssertTrue(result.ignoreAppBlocksMemory)
        XCTAssertTrue(result.displayOnlyPointing)
    }

    func testPermissionSmokeIsReadOnlyWhenPermissionsAreDenied() {
        let deniedProbe = NativeCapturePermissionProbe(
            screenRecordingPreflight: false,
            accessibilityTrusted: false,
            promptRequested: false
        )
        let result = NativeCapturePermissionSmokeResult.run(
            probe: deniedProbe,
            checkedAt: Date(timeIntervalSince1970: 0)
        )

        XCTAssertTrue(result.passed)
        XCTAssertEqual(result.benchmarkID, nativeCapturePermissionSmokeBenchmarkID)
        XCTAssertEqual(result.policyRef, nativeCapturePermissionSmokePolicyRef)
        XCTAssertFalse(result.screenRecordingPreflight)
        XCTAssertFalse(result.accessibilityTrusted)
        XCTAssertFalse(result.promptRequested)
        XCTAssertFalse(result.captureStarted)
        XCTAssertFalse(result.accessibilityObserverStarted)
        XCTAssertFalse(result.memoryWriteAllowed)
        XCTAssertTrue(result.evidenceRefs.isEmpty)
        XCTAssertEqual(result.allowedEffects, ["read_permission_status"])
        XCTAssertTrue(result.blockedEffects.contains("request_screen_recording_permission"))
        XCTAssertTrue(result.blockedEffects.contains("start_screen_capture"))
    }

    func testCurrentProcessPermissionProbeDoesNotPrompt() {
        let probe = NativeCapturePermissionProbe.readCurrentProcess()

        XCTAssertFalse(probe.promptRequested)
    }

    func testNativeCursorFollowConfigIsDisplayOnlyAndBounded() throws {
        let config = try NativeCursorFollowConfig().validated()

        XCTAssertEqual(config.policyRef, nativeCursorFollowPolicyRef)
        XCTAssertTrue(config.displayOnly)
        XCTAssertTrue(config.ignoresMouseEvents)
        XCTAssertTrue(config.allowedEffects.contains("read_global_cursor_position"))
        XCTAssertTrue(config.blockedEffects.contains("start_screen_capture"))
        XCTAssertTrue(config.blockedEffects.contains("execute_click"))
        XCTAssertTrue(config.blockedEffects.contains("write_memory"))
    }

    func testNativeCursorFollowSmokeUsesOnlyCursorSamples() throws {
        let result = try NativeCursorFollowSmokeResult.run(
            samples: [
                NativeCursorSample(x: 10, y: 20, timestamp: Date(timeIntervalSince1970: 0)),
                NativeCursorSample(x: 15, y: 25, timestamp: Date(timeIntervalSince1970: 0.1)),
            ],
            checkedAt: Date(timeIntervalSince1970: 0)
        )

        XCTAssertTrue(result.passed)
        XCTAssertEqual(result.benchmarkID, nativeCursorFollowBenchmarkID)
        XCTAssertEqual(result.policyRef, nativeCursorFollowPolicyRef)
        XCTAssertTrue(result.displayOnly)
        XCTAssertFalse(result.captureStarted)
        XCTAssertFalse(result.accessibilityObserverStarted)
        XCTAssertFalse(result.memoryWriteAllowed)
        XCTAssertFalse(result.rawRefRetained)
        XCTAssertTrue(result.externalEffects.isEmpty)
        XCTAssertTrue(result.overlaySpec.ignoresMouseEventsByDefault)
    }

    func testScreenCaptureProbeDoesNotCaptureWithoutExplicitFlag() {
        let result = NativeScreenCaptureProbeResult.run(
            allowRealCapture: false,
            probe: NativeCapturePermissionProbe(
                screenRecordingPreflight: true,
                accessibilityTrusted: false,
                promptRequested: false
            ),
            checkedAt: Date(timeIntervalSince1970: 0),
            frameProvider: { NativeScreenFrameMetadata(width: 1440, height: 900) }
        )

        XCTAssertTrue(result.passed)
        XCTAssertEqual(result.benchmarkID, nativeScreenCaptureProbeBenchmarkID)
        XCTAssertFalse(result.captureAttempted)
        XCTAssertFalse(result.frameCaptured)
        XCTAssertFalse(result.rawPixelsReturned)
        XCTAssertFalse(result.rawRefRetained)
        XCTAssertFalse(result.memoryWriteAllowed)
        XCTAssertTrue(result.evidenceRefs.isEmpty)
        XCTAssertEqual(result.allowedEffects, ["read_permission_status"])
    }

    func testScreenCaptureProbeCapturesMetadataOnlyWhenExplicitlyAllowed() {
        let result = NativeScreenCaptureProbeResult.run(
            allowRealCapture: true,
            probe: NativeCapturePermissionProbe(
                screenRecordingPreflight: true,
                accessibilityTrusted: false,
                promptRequested: false
            ),
            checkedAt: Date(timeIntervalSince1970: 0),
            frameProvider: { NativeScreenFrameMetadata(width: 1440, height: 900) }
        )

        XCTAssertTrue(result.passed)
        XCTAssertTrue(result.captureAttempted)
        XCTAssertTrue(result.frameCaptured)
        XCTAssertEqual(result.frameWidth, 1440)
        XCTAssertEqual(result.frameHeight, 900)
        XCTAssertFalse(result.rawPixelsReturned)
        XCTAssertFalse(result.rawRefRetained)
        XCTAssertFalse(result.memoryWriteAllowed)
        XCTAssertTrue(result.blockedEffects.contains("return_raw_pixels"))
        XCTAssertTrue(result.blockedEffects.contains("store_raw_evidence"))
    }
}
