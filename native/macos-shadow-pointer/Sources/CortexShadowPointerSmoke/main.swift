import CortexShadowPointerNative
import Foundation

do {
    let result = try ShadowPointerNativeSmokeResult.run()
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(result)
    print(String(decoding: data, as: UTF8.self))
    if !result.passed {
        exit(1)
    }
} catch {
    fputs("Shadow Pointer native smoke failed: \(error)\n", stderr)
    exit(1)
}
