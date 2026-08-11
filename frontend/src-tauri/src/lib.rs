#[cfg(target_os = "linux")]
use tauri::Manager;

#[cfg(target_os = "linux")]
mod linux_permissions;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_macos_permissions::init())
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      #[cfg(target_os = "linux")]
      for (_, webview) in app.webview_windows() {
        linux_permissions::enable_media_permissions(webview.as_ref())?;
      }

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
