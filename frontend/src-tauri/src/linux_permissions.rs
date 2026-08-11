//! Enables microphone/camera access for WebKitGTK.
//!
//! WebKitGTK auto-denies `getUserMedia` unless the app both enables the
//! `enable-media-stream`/`enable-webrtc` settings and answers the
//! `permission-request` signal. wry's webkitgtk backend does neither
//! (see tauri#14753), so we do it here on Linux only; macOS and Windows
//! handle media permissions in the webview engine itself.

use tauri::Webview;
use webkit2gtk::glib::prelude::Cast;
use webkit2gtk::{PermissionRequestExt, SettingsExt, WebViewExt};

/// Grants media-stream and webrtc capabilities and auto-answers
/// permission requests for user-media; all other permission requests
/// (geolocation, notifications, ...) are explicitly denied.
pub(crate) fn enable_media_permissions(webview: &Webview) -> tauri::Result<()> {
  webview.with_webview(|platform_webview| {
    let webview = platform_webview.inner();

    if let Some(settings) = webview.settings() {
      settings.set_enable_media_stream(true);
      settings.set_enable_webrtc(true);
    }

    webview.connect_permission_request(|_, request| {
      if request
        .downcast_ref::<webkit2gtk::UserMediaPermissionRequest>()
        .is_some()
      {
        request.allow();
      } else {
        request.deny();
      }
      true
    });
  })
}
