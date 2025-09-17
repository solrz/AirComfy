//
//  ContentView.swift
//  AirComfy
//
//  Created by App開發 on 2025/9/17.
//

import SwiftUI
import WebKit

struct ContentView: View {
    var body: some View {
        WebViewContainer()
            .ignoresSafeArea()
    }
}

struct WebViewContainer: UIViewRepresentable {
    typealias UIViewType = WKWebView

    func makeUIView(context: Context) -> WKWebView {
        let webView = createConfiguredWebView()
        webView.navigationDelegate = context.coordinator
        loadMainHTML(in: webView)
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    func makeCoordinator() -> WebViewCoordinator {
        WebViewCoordinator()
    }

    private func createConfiguredWebView() -> WKWebView {
        let configuration = WKWebViewConfiguration()
        setupWebViewConfiguration(configuration)
        return WKWebView(frame: .zero, configuration: configuration)
    }

    private func setupWebViewConfiguration(_ configuration: WKWebViewConfiguration) {
        configuration.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        configuration.setValue(true, forKey: "allowUniversalAccessFromFileURLs")
        configuration.setURLSchemeHandler(CORSHandler(), forURLScheme: "comfyproxy")
    }

    private func loadMainHTML(in webView: WKWebView) {
        guard let htmlPath = Bundle.main.path(forResource: "index", ofType: "html") else {
            print("ERROR: Could not find index.html in bundle")
            return
        }

        let htmlURL = URL(fileURLWithPath: htmlPath)
        print("Loading HTML from: \(htmlURL)")
        webView.loadFileURL(htmlURL, allowingReadAccessTo: htmlURL.deletingLastPathComponent())
    }
}

final class WebViewCoordinator: NSObject, WKNavigationDelegate {
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else {
            decisionHandler(.cancel)
            return
        }

        print("Navigation to: \(url)")
        decisionHandler(.allow)
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        print("Page loaded successfully")
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("Page load failed: \(error)")
    }
}

#Preview {
    ContentView()
}
