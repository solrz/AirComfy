import Foundation
import WebKit

final class CORSHandler: NSObject, WKURLSchemeHandler {
    private enum Constants {
        static let scheme = "comfyproxy://"
        static let replacement = "http://"
        static let corsHeaders = [
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        ]
    }

    private enum HandlerError: Error {
        case invalidURL
        case invalidTargetURL
        case invalidResponse
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        do {
            let request = try buildProxiedRequest(from: urlSchemeTask.request)
            executeRequest(request, for: urlSchemeTask)
        } catch {
            urlSchemeTask.didFailWithError(error)
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

    private func buildProxiedRequest(from originalRequest: URLRequest) throws -> URLRequest {
        guard let url = originalRequest.url else { throw HandlerError.invalidURL }

        let targetURLString = url.absoluteString.replacingOccurrences(
            of: Constants.scheme,
            with: Constants.replacement
        )

        guard let targetURL = URL(string: targetURLString) else {
            throw HandlerError.invalidTargetURL
        }

        var request = URLRequest(url: targetURL)
        request.httpMethod = originalRequest.httpMethod ?? "GET"
        request.timeoutInterval = 30.0

        // Copy headers
        if let headers = originalRequest.allHTTPHeaderFields {
            for (key, value) in headers {
                request.setValue(value, forHTTPHeaderField: key)
            }
        }

        // Handle POST body
        if let bodyData = originalRequest.httpBody {
            request.httpBody = bodyData
        } else if let bodyStream = originalRequest.httpBodyStream {
            // Handle streamed body
            bodyStream.open()
            let bufferSize = 1024
            let buffer = UnsafeMutablePointer<UInt8>.allocate(capacity: bufferSize)
            defer {
                buffer.deallocate()
                bodyStream.close()
            }

            var bodyData = Data()
            while bodyStream.hasBytesAvailable {
                let bytesRead = bodyStream.read(buffer, maxLength: bufferSize)
                if bytesRead > 0 {
                    bodyData.append(buffer, count: bytesRead)
                }
            }
            request.httpBody = bodyData
        }

        return request
    }

    private func executeRequest(_ request: URLRequest, for urlSchemeTask: WKURLSchemeTask) {
        print("CORSHandler: Executing request to \(request.url?.absoluteString ?? "unknown")")
        print("CORSHandler: Method: \(request.httpMethod ?? "GET")")
        print("CORSHandler: Headers: \(request.allHTTPHeaderFields ?? [:])")

        if let body = request.httpBody {
            print("CORSHandler: Body size: \(body.count) bytes")
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("CORSHandler: Request failed with error: \(error)")
                urlSchemeTask.didFailWithError(error)
                return
            }

            print("CORSHandler: Response received")
            if let httpResponse = response as? HTTPURLResponse {
                print("CORSHandler: Status code: \(httpResponse.statusCode)")
            }

            do {
                let modifiedResponse = try self.addCORSHeaders(to: response)
                urlSchemeTask.didReceive(modifiedResponse)

                if let data = data {
                    print("CORSHandler: Sending \(data.count) bytes of data")
                    urlSchemeTask.didReceive(data)
                }

                urlSchemeTask.didFinish()
                print("CORSHandler: Request completed successfully")
            } catch {
                print("CORSHandler: Failed to process response: \(error)")
                urlSchemeTask.didFailWithError(error)
            }
        }.resume()
    }

    private func addCORSHeaders(to response: URLResponse?) throws -> HTTPURLResponse {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw HandlerError.invalidResponse
        }

        var headers = httpResponse.allHeaderFields as? [String: String] ?? [:]
        Constants.corsHeaders.forEach { key, value in
            headers[key] = value
        }

        guard let modifiedResponse = HTTPURLResponse(
            url: httpResponse.url!,
            statusCode: httpResponse.statusCode,
            httpVersion: nil,
            headerFields: headers
        ) else {
            throw HandlerError.invalidResponse
        }

        return modifiedResponse
    }
}