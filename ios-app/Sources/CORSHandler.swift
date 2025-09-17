//
//  CORSHandler.swift
//  AirComfy
//
//  Created by App開發 on 2025/9/17.
//

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
        request.httpMethod = originalRequest.httpMethod
        request.allHTTPHeaderFields = originalRequest.allHTTPHeaderFields
        request.httpBody = originalRequest.httpBody

        Constants.corsHeaders.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }

        return request
    }

    private func executeRequest(_ request: URLRequest, for urlSchemeTask: WKURLSchemeTask) {
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                urlSchemeTask.didFailWithError(error)
                return
            }

            do {
                let modifiedResponse = try self.addCORSHeaders(to: response)
                urlSchemeTask.didReceive(modifiedResponse)

                if let data = data {
                    urlSchemeTask.didReceive(data)
                }

                urlSchemeTask.didFinish()
            } catch {
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