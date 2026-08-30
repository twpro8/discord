defmodule CallServerWeb.CallChannel do
  use Phoenix.Channel

  require Logger

  # Unified room: room:{id} primary, call:{id} alias for backwards compat.
  @impl true
  def join("room:" <> room_id, _params, socket) do
    Logger.info("Joining room channel #{room_id}")
    {:ok, socket |> assign(:room_id, room_id)}
  end

  @impl true
  def join("call:" <> call_id, _params, socket) do
    Logger.info("Joining call channel #{call_id} (alias for room)")
    {:ok, socket |> assign(:room_id, call_id)}
  end

  @impl true
  def handle_in("offer", %{"sdp" => sdp} = payload, socket) do
    from = socket.assigns[:user_id] || payload["from"]
    broadcast_from!(socket, "offer", %{sdp: sdp, from: from})
    {:noreply, socket}
  end

  @impl true
  def handle_in("answer", %{"sdp" => sdp} = payload, socket) do
    from = socket.assigns[:user_id] || payload["from"]
    broadcast_from!(socket, "answer", %{sdp: sdp, from: from})
    {:noreply, socket}
  end

  @impl true
  def handle_in("ice_candidate", %{"candidate" => candidate} = payload, socket) do
    from = socket.assigns[:user_id] || payload["from"]
    broadcast_from!(socket, "ice_candidate", %{candidate: candidate, from: from})
    {:noreply, socket}
  end

  @impl true
  def handle_in("screen_share_started", payload, socket) do
    from = socket.assigns[:user_id] || payload["from"]
    broadcast_from!(socket, "screen_share_started", %{from: from, enabled: true})
    {:noreply, socket}
  end

  @impl true
  def handle_in("screen_share_ended", payload, socket) do
    from = socket.assigns[:user_id] || payload["from"]
    broadcast_from!(socket, "screen_share_ended", %{from: from, enabled: false})
    {:noreply, socket}
  end
end
