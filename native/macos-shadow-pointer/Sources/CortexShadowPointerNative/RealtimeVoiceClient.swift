import Foundation
import AVFoundation

public extension Notification.Name {
    static let realtimeAudioAmplitudeUpdated = Notification.Name("RealtimeAudioAmplitudeUpdated")
    static let realtimeConnectionError = Notification.Name("RealtimeConnectionError")
    static let realtimeConnectionRestored = Notification.Name("RealtimeConnectionRestored")
}

public struct RealtimeReconnectPolicy: Equatable, Sendable {
    public var maxAttempts: Int
    public var initialDelay: TimeInterval
    public var maxDelay: TimeInterval

    public init(maxAttempts: Int = 5, initialDelay: TimeInterval = 0.75, maxDelay: TimeInterval = 8.0) {
        self.maxAttempts = max(1, maxAttempts)
        self.initialDelay = max(0.1, initialDelay)
        self.maxDelay = max(self.initialDelay, maxDelay)
    }

    public func delay(forAttempt attempt: Int) -> TimeInterval {
        let exponent = max(0, attempt - 1)
        let candidate = initialDelay * pow(2.0, Double(exponent))
        return min(candidate, maxDelay)
    }
}

@available(macOS 13.0, *)
public final class RealtimeVoiceClient: NSObject, URLSessionWebSocketDelegate, @unchecked Sendable {
    public static let shared = RealtimeVoiceClient()
    public static let nativeMouseToolNames = [
        "move_mouse",
        "click_mouse",
        "right_click_mouse",
        "double_click_mouse",
        "drag_mouse",
        "scroll_mouse",
    ]

    private var webSocket: URLSessionWebSocketTask?
    private var isConnected = false
    private lazy var session: URLSession = {
        URLSession(configuration: .default, delegate: self, delegateQueue: nil)
    }()
    private var manuallyDisconnected = false
    private var reconnectAttempt = 0
    private var connectCompletion: ((Bool, String?) -> Void)?
    private var suppressReconnectForCurrentSocket = false
    public var reconnectPolicy = RealtimeReconnectPolicy()

    private let audioEngine = AVAudioEngine()
    private var audioFormat: AVAudioFormat?
    private var converter: AVAudioConverter?

    private var pendingItems: [[String: Any]] = []

    public var onMessageReceived: (([String: Any]) -> Void)?
    public var onToolCallReceived: ((String, String, [String: Any]) -> Void)?
    public var onAudioPlayback: ((Data) -> Void)?

    public override init() {
        super.init()
        setupAudioEngine()
    }

    // MARK: - Token Fetching

    public func fetchTokenAndConnect(completion: @escaping (Bool, String?) -> Void) {
        manuallyDisconnected = false
        reconnectAttempt = 0
        connectCompletion = completion
        fetchTokenAndConnectAttempt()
    }

    private func fetchTokenAndConnectAttempt() {
        guard let url = URL(string: "http://127.0.0.1:8797/realtime-token") else {
            reportConnectionFailure("Invalid token endpoint URL", retry: false)
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"

        let task = session.dataTask(with: request) { [weak self] data, response, error in
            guard let self else { return }
            if let error = error {
                self.reportConnectionFailure(error.localizedDescription, retry: true)
                return
            }

            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                self.reportConnectionFailure("Invalid token response", retry: true)
                return
            }

            var token: String? = nil
            if let clientSecret = json["client_secret"] as? [String: Any], let val = clientSecret["value"] as? String {
                token = val
            } else if let val = json["value"] as? String {
                token = val
            }

            guard let validToken = token else {
                self.reportConnectionFailure("Token not found in response JSON", retry: true)
                return
            }

            let model = Self.realtimeModel(from: json)
            self.connectWebSocket(token: validToken, model: model)
        }
        task.resume()
    }

    // MARK: - WebSocket Connection

    private func connectWebSocket(token: String, model: String) {
        guard let encodedModel = model.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) else {
            reportConnectionFailure("Invalid realtime model name", retry: false)
            return
        }
        let urlString = "wss://api.openai.com/v1/realtime?model=\(encodedModel)"
        guard let url = URL(string: urlString) else { return }

        var request = URLRequest(url: url)
        request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        suppressReconnectForCurrentSocket = false
        webSocket = session.webSocketTask(with: request)
        webSocket?.resume()
    }

    public func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didOpenWithProtocol protocol: String?
    ) {
        isConnected = true
        reconnectAttempt = 0
        DispatchQueue.main.async {
            NotificationCenter.default.post(name: .realtimeConnectionRestored, object: nil)
        }

        receiveMessage()

        // Define initial session state (e.g. tool registration)
        sendSessionUpdate()
        connectCompletion?(true, nil)
        connectCompletion = nil
    }

    public func urlSession(
        _ session: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didCloseWith closeCode: URLSessionWebSocketTask.CloseCode,
        reason: Data?
    ) {
        isConnected = false
        guard !manuallyDisconnected else { return }
        let shouldRetry = closeCode.rawValue != 4000
        suppressReconnectForCurrentSocket = !shouldRetry
        reportConnectionFailure("Realtime WebSocket closed: \(closeCode.rawValue)", retry: shouldRetry)
    }

    public static func realtimeModel(from tokenResponse: [String: Any]) -> String {
        if let session = tokenResponse["session"] as? [String: Any],
           let model = session["model"] as? String,
           !model.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return model
        }
        if let model = tokenResponse["model"] as? String,
           !model.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            return model
        }
        return "gpt-realtime-2"
    }

    public func disconnect() {
        manuallyDisconnected = true
        webSocket?.cancel(with: .goingAway, reason: nil)
        isConnected = false
        stopListening()
    }

    private func sendSessionUpdate() {
        let sessionUpdate: [String: Any] = [
            "type": "session.update",
            "session": [
                "type": "realtime",
                "instructions": (
                    "You are Cortex Pointer. Prefer native pointer tools for simple, safe, "
                    + "user-requested mouse guidance. Keep replies brief and text-only."
                ),
                "tools": Self.realtimeToolDefinitions(),
                "tool_choice": "auto"
            ]
        ]
        send(json: sessionUpdate)
    }

    // MARK: - Messaging

    private func receiveMessage() {
        webSocket?.receive { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    self.handleWebSocketString(text)
                case .data(let data):
                    print("Received binary data of size: \(data.count)")
                @unknown default:
                    break
                }
                if self.isConnected {
                    self.receiveMessage()
                }
            case .failure(let error):
                print("WebSocket receive error: \(error)")
                self.isConnected = false
                self.reportConnectionFailure(
                    error.localizedDescription,
                    retry: !self.suppressReconnectForCurrentSocket
                )
            }
        }
    }

    private func handleWebSocketString(_ text: String) {
        guard let data = text.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return }

        onMessageReceived?(json)

        guard let type = json["type"] as? String else { return }

        if type == "response.function_call_arguments.done" {
            if let name = json["name"] as? String,
               let callId = json["call_id"] as? String,
               let argsString = json["arguments"] as? String,
               let argsData = argsString.data(using: .utf8),
               let args = try? JSONSerialization.jsonObject(with: argsData) as? [String: Any] {
                DispatchQueue.main.async {
                    self.onToolCallReceived?(name, callId, args)
                }
            }
        } else if type == "error" {
            let errorPayload = json["error"] as? [String: Any]
            let message = errorPayload?["message"] as? String
                ?? json["message"] as? String
                ?? "Realtime API returned an error"
            if message.localizedCaseInsensitiveContains("no longer supported") {
                suppressReconnectForCurrentSocket = true
            }
            DispatchQueue.main.async {
                NotificationCenter.default.post(
                    name: .realtimeConnectionError,
                    object: nil,
                    userInfo: ["message": message]
                )
            }
        } else if type == "response.text.delta" {
            if let delta = json["delta"] as? String {
                DispatchQueue.main.async {
                    NotificationCenter.default.post(
                        name: Notification.Name("RealtimeTextDeltaReceived"),
                        object: nil,
                        userInfo: ["delta": delta]
                    )
                }
            }
        } else if type == "response.text.done" {
            if let textVal = json["text"] as? String {
                DispatchQueue.main.async {
                    NotificationCenter.default.post(
                        name: Notification.Name("RealtimeTextDoneReceived"),
                        object: nil,
                        userInfo: ["text": textVal]
                    )
                }
            }
        }
    }

    public func sendToolOutput(callId: String, output: [String: Any]) {
        guard let outputData = try? JSONSerialization.data(withJSONObject: output),
              let outputString = String(data: outputData, encoding: .utf8) else { return }

        let itemCreateMsg: [String: Any] = [
            "type": "conversation.item.create",
            "item": [
                "type": "function_call_output",
                "call_id": callId,
                "output": outputString
            ]
        ]
        send(json: itemCreateMsg)
        send(json: Self.responseCreateMessage())
    }

    public static func responseCreateMessage() -> [String: Any] {
        ["type": "response.create"]
    }

    private func send(json: [String: Any]) {
        guard isConnected, let data = try? JSONSerialization.data(withJSONObject: json),
              let string = String(data: data, encoding: .utf8) else { return }
        webSocket?.send(.string(string)) { error in
            if let error = error {
                print("WebSocket send error: \(error)")
                self.reportConnectionFailure(error.localizedDescription, retry: true)
            }
        }
    }

    // MARK: - Audio Capture (Push-To-Talk)

    private func setupAudioEngine() {
        let inputNode = audioEngine.inputNode
        let inputFormat = inputNode.inputFormat(forBus: 0)

        // OpenAI Realtime requires 24kHz Mono PCM, 16-bit
        audioFormat = AVAudioFormat(commonFormat: .pcmFormatInt16,
                                    sampleRate: 24000,
                                    channels: 1,
                                    interleaved: false)

        guard let audioFormat = audioFormat else { return }

        converter = AVAudioConverter(from: inputFormat, to: audioFormat)

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: inputFormat) { [weak self] buffer, time in
            self?.processAudioBuffer(buffer: buffer)
        }
    }

    public func startListening() {
        do {
            try audioEngine.start()
        } catch {
            print("Audio engine start failed: \(error)")
        }
    }

    public func stopListening() {
        audioEngine.stop()

        // Send a message indicating audio input is complete to trigger a response
        let commitMsg: [String: Any] = [
            "type": "input_audio_buffer.commit"
        ]
        send(json: commitMsg)

        send(json: Self.responseCreateMessage())
    }

    private func processAudioBuffer(buffer: AVAudioPCMBuffer) {
        guard let converter = converter, let audioFormat = audioFormat else { return }
        let amplitude = Self.normalizedRMSAmplitude(from: buffer)
        DispatchQueue.main.async {
            NotificationCenter.default.post(
                name: .realtimeAudioAmplitudeUpdated,
                object: nil,
                userInfo: ["amplitude": amplitude]
            )
        }

        let frameCapacity = AVAudioFrameCount(audioFormat.sampleRate / buffer.format.sampleRate * Double(buffer.frameLength))
        guard let pcmBuffer = AVAudioPCMBuffer(pcmFormat: audioFormat, frameCapacity: frameCapacity) else { return }

        var error: NSError?
        let inputBlock: AVAudioConverterInputBlock = { inNumPackets, outStatus in
            outStatus.pointee = AVAudioConverterInputStatus.haveData
            return buffer
        }

        converter.convert(to: pcmBuffer, error: &error, withInputFrom: inputBlock)

        if let channelData = pcmBuffer.int16ChannelData {
            let dataSize = Int(pcmBuffer.frameLength) * 2 // 16-bit = 2 bytes per frame
            let data = Data(bytes: channelData[0], count: dataSize)
            let base64String = data.base64EncodedString()

            let msg: [String: Any] = [
                "type": "input_audio_buffer.append",
                "audio": base64String
            ]
            send(json: msg)
        }
    }

    public static func normalizedRMSAmplitude(from buffer: AVAudioPCMBuffer) -> Float {
        let frameLength = Int(buffer.frameLength)
        guard frameLength > 0 else { return 0 }

        if let floatData = buffer.floatChannelData {
            let channelCount = max(1, Int(buffer.format.channelCount))
            var sumSquares: Float = 0
            var sampleCount = 0
            for channel in 0..<channelCount {
                let samples = floatData[channel]
                for index in 0..<frameLength {
                    let sample = samples[index]
                    sumSquares += sample * sample
                    sampleCount += 1
                }
            }
            guard sampleCount > 0 else { return 0 }
            return min(1, max(0, sqrt(sumSquares / Float(sampleCount))))
        }

        if let int16Data = buffer.int16ChannelData {
            let channelCount = max(1, Int(buffer.format.channelCount))
            var sumSquares: Double = 0
            var sampleCount = 0
            for channel in 0..<channelCount {
                let samples = int16Data[channel]
                for index in 0..<frameLength {
                    let normalized = Double(samples[index]) / Double(Int16.max)
                    sumSquares += normalized * normalized
                    sampleCount += 1
                }
            }
            guard sampleCount > 0 else { return 0 }
            return Float(min(1, max(0, sqrt(sumSquares / Double(sampleCount)))))
        }

        return 0
    }

    public static func realtimeToolDefinitions() -> [[String: Any]] {
        [
            [
                "type": "function",
                "name": "explain_target",
                "description": "Explains a target on screen. Returns a visual text chip instead of speaking.",
                "parameters": [
                    "type": "object",
                    "properties": [
                        "target_id": [
                            "type": "string",
                            "description": "ID of the target to explain",
                        ],
                    ],
                    "required": ["target_id"],
                ],
            ],
            nativePointerTool(
                name: "move_mouse",
                description: "Moves the system mouse pointer natively to specific screen coordinates.",
                required: ["x", "y"]
            ),
            nativePointerTool(
                name: "click_mouse",
                description: "Performs a native left mouse click at the current position or at specific screen coordinates.",
                required: []
            ),
            nativePointerTool(
                name: "right_click_mouse",
                description: "Performs a native right mouse click at specific screen coordinates.",
                required: ["x", "y"]
            ),
            nativePointerTool(
                name: "double_click_mouse",
                description: "Performs a native double left-click at specific screen coordinates.",
                required: ["x", "y"]
            ),
            [
                "type": "function",
                "name": "drag_mouse",
                "description": "Performs a smooth native drag from one screen coordinate to another.",
                "parameters": [
                    "type": "object",
                    "properties": [
                        "fromX": ["type": "number", "description": "Starting X coordinate in AppKit screen pixels."],
                        "fromY": ["type": "number", "description": "Starting Y coordinate in AppKit screen pixels."],
                        "toX": ["type": "number", "description": "Ending X coordinate in AppKit screen pixels."],
                        "toY": ["type": "number", "description": "Ending Y coordinate in AppKit screen pixels."],
                    ],
                    "required": ["fromX", "fromY", "toX", "toY"],
                ],
            ],
            [
                "type": "function",
                "name": "scroll_mouse",
                "description": "Performs native two-dimensional scrolling.",
                "parameters": [
                    "type": "object",
                    "properties": [
                        "dx": ["type": "number", "description": "Horizontal scroll delta."],
                        "dy": ["type": "number", "description": "Vertical scroll delta."],
                    ],
                    "required": ["dx", "dy"],
                ],
            ],
        ]
    }

    private static func nativePointerTool(
        name: String,
        description: String,
        required: [String]
    ) -> [String: Any] {
        [
            "type": "function",
            "name": name,
            "description": description,
            "parameters": [
                "type": "object",
                "properties": [
                    "x": ["type": "number", "description": "X coordinate in AppKit screen pixels."],
                    "y": ["type": "number", "description": "Y coordinate in AppKit screen pixels."],
                ],
                "required": required,
            ],
        ]
    }

    private func reportConnectionFailure(_ message: String, retry: Bool) {
        isConnected = false
        DispatchQueue.main.async {
            NotificationCenter.default.post(
                name: .realtimeConnectionError,
                object: nil,
                userInfo: ["message": message]
            )
        }
        guard retry, !manuallyDisconnected else {
            connectCompletion?(false, message)
            connectCompletion = nil
            return
        }
        scheduleReconnect(after: message)
    }

    private func scheduleReconnect(after message: String) {
        guard reconnectAttempt < reconnectPolicy.maxAttempts else {
            connectCompletion?(false, message)
            connectCompletion = nil
            return
        }
        reconnectAttempt += 1
        let delay = reconnectPolicy.delay(forAttempt: reconnectAttempt)
        DispatchQueue.global(qos: .utility).asyncAfter(deadline: .now() + delay) { [weak self] in
            guard let self, !self.manuallyDisconnected else { return }
            self.fetchTokenAndConnectAttempt()
        }
    }
}
