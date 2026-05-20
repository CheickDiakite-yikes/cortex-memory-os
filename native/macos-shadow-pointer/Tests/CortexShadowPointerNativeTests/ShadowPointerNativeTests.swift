import XCTest
import AVFoundation
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
        XCTAssertEqual(config.sampleHz, 60)
        XCTAssertTrue(config.followsSystemWide)
        XCTAssertEqual(config.surfaceScope, "system_wide_macos")
        XCTAssertEqual(config.coordinateSpace, "global_display_pixels")
        XCTAssertFalse(config.browserDependency)
        XCTAssertLessThanOrEqual(config.maxRenderLatencyMs, 24)
        XCTAssertLessThanOrEqual(config.maxPointerDriftPx, 18)
        XCTAssertEqual(config.bubbleAnchorStrategy, "cursor_adjacent_edge_aware")
        XCTAssertTrue(config.allowedEffects.contains("read_global_cursor_position"))
        XCTAssertTrue(config.allowedEffects.contains("anchor_response_bubble"))
        XCTAssertTrue(config.blockedEffects.contains("start_screen_capture"))
        XCTAssertTrue(config.blockedEffects.contains("execute_click"))
        XCTAssertTrue(config.blockedEffects.contains("move_system_cursor"))
        XCTAssertTrue(config.blockedEffects.contains("browser_only_tracking"))
        XCTAssertTrue(config.blockedEffects.contains("unanchored_response_bubble"))
        XCTAssertTrue(config.blockedEffects.contains("write_memory"))
    }

    func testNativeOverlayVisualSpecUsesSystemGlassAndLoadingStates() throws {
        let visual = try NativeOverlayVisualSpec().validated()

        XCTAssertEqual(visual.benchmarkID, nativeOverlayVisualPolishBenchmarkID)
        XCTAssertEqual(visual.policyRef, nativeOverlayVisualPolishPolicyRef)
        XCTAssertEqual(visual.visualStyle, "apple_liquid_glass_companion")
        XCTAssertEqual(visual.material, "hud_window_vibrant_material")
        XCTAssertTrue(visual.vibrancyEnabled)
        XCTAssertTrue(visual.tintSemanticOnly)
        XCTAssertEqual(visual.cursorShape, "secondary_arrow")
        XCTAssertTrue(visual.cursorHotspotVisible)
        XCTAssertEqual(visual.loadingAnimation, "three_dot_breathing")
        XCTAssertEqual(visual.loadingDotCount, 3)
        XCTAssertGreaterThanOrEqual(visual.loadingFrameRateHz, 24)
        XCTAssertTrue(visual.animationRespectsReducedMotion)
        XCTAssertLessThanOrEqual(visual.maxTextLines, 2)
        XCTAssertEqual(visual.foregroundStyle, "vibrant_label_and_secondary_label")
        XCTAssertTrue(visual.avoidsOpaqueScrim)
        XCTAssertTrue(visual.glassElementsGrouped)
        XCTAssertTrue(visual.displayOnly)
        XCTAssertTrue(visual.blockedEffects.contains("execute_click"))
        XCTAssertTrue(visual.blockedEffects.contains("start_screen_capture"))
    }

    func testNativeAgenticPointerCardIsSafeAndBounded() throws {
        let card = try NativeAgenticPointerCard().validated()

        XCTAssertEqual(card.benchmarkID, nativeAgenticPointerCardBenchmarkID)
        XCTAssertEqual(card.policyRef, nativeAgenticPointerCardPolicyRef)
        XCTAssertEqual(card.title, "Draft the next steps")
        XCTAssertEqual(card.targetLabel, "Color Page")
        XCTAssertEqual(card.routeKind, "draft_only")
        XCTAssertTrue(card.displayOnly)
        XCTAssertFalse(card.memoryWriteAllowed)
        XCTAssertFalse(card.rawRefRetained)
        XCTAssertFalse(card.externalEffectEnabled)
        XCTAssertLessThanOrEqual(card.title.count, 44)
        XCTAssertLessThanOrEqual(card.message.count, 82)
        XCTAssertTrue(card.blockedEffects.contains("execute_click"))
        XCTAssertTrue(card.blockedEffects.contains("type_text"))
        XCTAssertTrue(card.blockedEffects.contains("write_memory_without_review"))
    }

    func testNativeAgenticPointerCardRejectsSecretsAndEffects() {
        XCTAssertThrowsError(
            try NativeAgenticPointerCard(message: "OPENAI_API_KEY should never show").validated()
        )
        XCTAssertThrowsError(
            try NativeAgenticPointerCard(displayOnly: false).validated()
        )
        XCTAssertThrowsError(
            try NativeAgenticPointerCard(blockedEffects: ["execute_click"]).validated()
        )
    }

    func testNativeCursorFollowSmokeUsesOnlyCursorSamples() throws {
        let result = try NativeCursorFollowSmokeResult.run(
            samples: [
                NativeCursorSample(x: 120, y: 160, timestamp: Date(timeIntervalSince1970: 0)),
                NativeCursorSample(x: 150, y: 190, timestamp: Date(timeIntervalSince1970: 0.1)),
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
        XCTAssertEqual(result.visualSpec.visualStyle, "apple_liquid_glass_companion")
        XCTAssertEqual(result.visualSpec.material, "hud_window_vibrant_material")
        XCTAssertEqual(result.visualSpec.loadingAnimation, "three_dot_breathing")
        XCTAssertTrue(result.visualSpec.avoidsOpaqueScrim)
        XCTAssertTrue(result.systemWideReady)
        XCTAssertFalse(result.browserDependency)
        XCTAssertLessThanOrEqual(result.sampleIntervalMs, result.config.maxRenderLatencyMs)
        XCTAssertLessThanOrEqual(result.maxPointerDriftPxMeasured, result.config.maxPointerDriftPx)
        XCTAssertTrue(result.bubbleAnchorReady)
        XCTAssertEqual(Set(result.placementSamples.map(\.bubbleAnchoredTo)), Set(["system_cursor"]))
    }

    func testNativeCursorPlacementAccountsForCursorHotspotAndEdges() throws {
        let config = try NativeCursorFollowConfig().validated()
        let display = NativeDisplayFrame(minX: 0, minY: 0, width: 400, height: 300)
        let overlay = NativeOverlaySize(width: 146, height: 68)
        let bubble = NativeBubbleSize(width: 160, height: 54)

        let middle = try NativeCursorPlacementEngine.place(
            sample: NativeCursorSample(x: 120, y: 160, timestamp: Date(timeIntervalSince1970: 0)),
            config: config,
            displayFrame: display,
            overlaySize: overlay,
            bubbleSize: bubble
        )
        XCTAssertEqual(middle.visualCursorX, middle.desiredCursorX, accuracy: 0.001)
        XCTAssertEqual(middle.visualCursorY, middle.desiredCursorY, accuracy: 0.001)
        XCTAssertLessThanOrEqual(middle.pointerDriftPx, config.maxPointerDriftPx)
        XCTAssertEqual(middle.bubbleAnchoredTo, "system_cursor")
        XCTAssertEqual(middle.bubbleSide, "right")

        let edge = try NativeCursorPlacementEngine.place(
            sample: NativeCursorSample(x: 386, y: 280, timestamp: Date(timeIntervalSince1970: 0)),
            config: config,
            displayFrame: display,
            overlaySize: overlay,
            bubbleSize: bubble
        )
        XCTAssertEqual(edge.bubbleSide, "left")
        XCTAssertGreaterThanOrEqual(edge.bubbleX, display.minX)
        XCTAssertLessThanOrEqual(edge.bubbleX + bubble.width, display.maxX)
        XCTAssertGreaterThanOrEqual(edge.bubbleY, display.minY)
        XCTAssertLessThanOrEqual(edge.bubbleY + bubble.height, display.maxY)
    }

    func testRealtimeVoiceClientRegistersFullNativePointerTools() throws {
        guard #available(macOS 13.0, *) else {
            throw XCTSkip("RealtimeVoiceClient requires macOS 13")
        }

        let tools = RealtimeVoiceClient.realtimeToolDefinitions()
        let names = Set(tools.compactMap { $0["name"] as? String })

        XCTAssertTrue(Set(RealtimeVoiceClient.nativeMouseToolNames).isSubset(of: names))
        XCTAssertTrue(names.contains("explain_target"))
        XCTAssertTrue(names.contains("right_click_mouse"))
        XCTAssertTrue(names.contains("double_click_mouse"))
        XCTAssertTrue(names.contains("drag_mouse"))
        XCTAssertTrue(names.contains("scroll_mouse"))
    }

    func testRealtimeAudioAmplitudeUsesRMSPower() throws {
        guard #available(macOS 13.0, *) else {
            throw XCTSkip("RealtimeVoiceClient requires macOS 13")
        }
        let format = AVAudioFormat(
            commonFormat: .pcmFormatFloat32,
            sampleRate: 48_000,
            channels: 1,
            interleaved: false
        )
        let buffer = AVAudioPCMBuffer(pcmFormat: try XCTUnwrap(format), frameCapacity: 4)
        let pcmBuffer = try XCTUnwrap(buffer)
        pcmBuffer.frameLength = 4
        let samples = try XCTUnwrap(pcmBuffer.floatChannelData?[0])
        samples[0] = 0
        samples[1] = 0.5
        samples[2] = -0.5
        samples[3] = 1

        let amplitude = RealtimeVoiceClient.normalizedRMSAmplitude(from: pcmBuffer)

        XCTAssertEqual(amplitude, sqrt(1.5 / 4), accuracy: 0.001)
    }

    func testRealtimeReconnectPolicyUsesBoundedExponentialBackoff() {
        let policy = RealtimeReconnectPolicy(maxAttempts: 5, initialDelay: 0.5, maxDelay: 2)

        XCTAssertEqual(policy.delay(forAttempt: 1), 0.5, accuracy: 0.001)
        XCTAssertEqual(policy.delay(forAttempt: 2), 1.0, accuracy: 0.001)
        XCTAssertEqual(policy.delay(forAttempt: 3), 2.0, accuracy: 0.001)
        XCTAssertEqual(policy.delay(forAttempt: 4), 2.0, accuracy: 0.001)
    }

    func testNativeChipPlacementClampsToVisibleFrameEdges() {
        let visible = NativeDisplayFrame(minX: 0, minY: 24, width: 400, height: 260)
        let topLeft = NativeChipPlacementEngine.place(
            cursorX: 2,
            cursorY: 278,
            chipWidth: 180,
            chipHeight: 70,
            visibleFrame: visible
        )
        let bottomRight = NativeChipPlacementEngine.place(
            cursorX: 398,
            cursorY: 26,
            chipWidth: 180,
            chipHeight: 70,
            visibleFrame: visible
        )

        XCTAssertGreaterThanOrEqual(topLeft.x, visible.minX + 10)
        XCTAssertLessThanOrEqual(topLeft.maxY, visible.maxY - 10)
        XCTAssertEqual(topLeft.side, "right")
        XCTAssertLessThanOrEqual(bottomRight.maxX, visible.maxX - 10)
        XCTAssertGreaterThanOrEqual(bottomRight.y, visible.minY + 10)
        XCTAssertEqual(bottomRight.side, "left")
    }

    func testNativeAnimationTimingSpecUsesDisplayLinkAndCubicEasing() throws {
        let spec = try NativeAnimationTimingSpec().validated()

        XCTAssertEqual(spec.benchmarkID, nativeCompanionHUDPhase2BenchmarkID)
        XCTAssertEqual(spec.policyRef, nativeCompanionHUDPhase2PolicyRef)
        XCTAssertEqual(spec.displayDriver, "CVDisplayLink")
        XCTAssertGreaterThanOrEqual(spec.targetRefreshHz, 60)
        XCTAssertEqual(spec.easingCurve, "cubic_ease_in_out")
        XCTAssertTrue(spec.amplitudeReactiveRing)
        XCTAssertEqual(spec.connectionErrorIndicator, "warm_amber_glass_chip")
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
        XCTAssertEqual(result.skipReason, "allow_real_capture_false")
        XCTAssertFalse(result.nextUserActions.isEmpty)
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
        XCTAssertNil(result.skipReason)
        XCTAssertEqual(result.frameWidth, 1440)
        XCTAssertEqual(result.frameHeight, 900)
        XCTAssertFalse(result.rawPixelsReturned)
        XCTAssertFalse(result.rawRefRetained)
        XCTAssertFalse(result.memoryWriteAllowed)
        XCTAssertTrue(result.blockedEffects.contains("return_raw_pixels"))
        XCTAssertTrue(result.blockedEffects.contains("store_raw_evidence"))
    }

    func testScreenCaptureProbeExplainsScreenRecordingPreflightSkip() {
        let result = NativeScreenCaptureProbeResult.run(
            allowRealCapture: true,
            probe: NativeCapturePermissionProbe(
                screenRecordingPreflight: false,
                accessibilityTrusted: false,
                promptRequested: false
            ),
            checkedAt: Date(timeIntervalSince1970: 0),
            frameProvider: { NativeScreenFrameMetadata(width: 1440, height: 900) }
        )

        XCTAssertTrue(result.passed)
        XCTAssertFalse(result.captureAttempted)
        XCTAssertFalse(result.frameCaptured)
        XCTAssertEqual(result.skipReason, "screen_recording_preflight_false")
        XCTAssertTrue(result.nextUserActions.first?.contains("Screen Recording") ?? false)
        XCTAssertFalse(result.rawPixelsReturned)
        XCTAssertFalse(result.rawRefRetained)
        XCTAssertFalse(result.memoryWriteAllowed)
    }
}
