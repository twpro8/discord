defmodule CallServerWeb.UserChannel do
  use Phoenix.Channel

  require Logger

  @impl true
  def join("user:" <> user_id, _params, socket) do
    Logger.info("User #{user_id} joined their channel")

    {:ok, socket |> assign(:user_id, user_id)}
  end

  # A calls B — unified room: room:{id} for 1:1, group, server voice.
  # Legacy single-target API kept as alias.
  @impl true
  def handle_in(
        "call_user",
        %{"target_user_id" => target_user_id},
        socket
      ) do
    caller_id = socket.assigns.user_id
    Logger.info("User #{caller_id} wants to call #{target_user_id}")
    room_id = UUID.uuid4()
    # TODO: Validate with Lumiere API
    # Broadcast both new room_id and legacy call_id for compat.
    CallServerWeb.Endpoint.broadcast(
      "user:#{target_user_id}",
      "incoming_call",
      %{
        caller_id: caller_id,
        call_id: room_id,
        room_id: room_id,
        participant_ids: [caller_id, target_user_id]
      }
    )

    {:reply, {:ok, %{status: "ringing", call_id: room_id, room_id: room_id}}, socket}
  end

  # Unified room creation for group / server-voice: create_room
  @impl true
  def handle_in(
        "create_room",
        %{"participant_ids" => participant_ids} = params,
        socket
      ) do
    caller_id = socket.assigns.user_id
    room_id = UUID.uuid4()
    type = params["type"] || "group"
    # Ensure caller in participants.
    all_ids = Enum.uniq([caller_id | participant_ids])
    Logger.info("User #{caller_id} creates #{type} room #{room_id} for #{inspect(all_ids)}")

    for target_id <- participant_ids, target_id != caller_id do
      CallServerWeb.Endpoint.broadcast(
        "user:#{target_id}",
        "incoming_call",
        %{
          caller_id: caller_id,
          call_id: room_id,
          room_id: room_id,
          participant_ids: all_ids,
          type: type
        }
      )
    end

    {:reply,
     {:ok, %{status: "ringing", room_id: room_id, call_id: room_id, participant_ids: all_ids}},
     socket}
  end

  # Invite additional peer to existing room (group / server)
  @impl true
  def handle_in(
        "invite_to_room",
        %{"room_id" => room_id, "user_id" => target_user_id},
        socket
      ) do
    caller_id = socket.assigns.user_id
    Logger.info("User #{caller_id} invites #{target_user_id} to room #{room_id}")

    CallServerWeb.Endpoint.broadcast(
      "user:#{target_user_id}",
      "incoming_call",
      %{
        caller_id: caller_id,
        call_id: room_id,
        room_id: room_id,
        invited_to_room: room_id
      }
    )

    {:reply, {:ok, %{status: "ringing", room_id: room_id}}, socket}
  end

  # Direct join for server voice channels: room:channel:{channelId}
  @impl true
  def handle_in("join_room", %{"room_id" => room_id}, socket) do
    Logger.info("User #{socket.assigns.user_id} joins room #{room_id}")
    {:reply, {:ok, %{status: "joined", room_id: room_id}}, socket}
  end

  @impl true
  def handle_in("decline_call", %{"caller_id" => caller_id}, socket) do
    target_user_id = socket.assigns.user_id

    CallServerWeb.Endpoint.broadcast(
      "user:#{caller_id}",
      "declined_call",
      %{
        target_user_id: target_user_id
      }
    )

    {:reply, {:ok, %{status: "finished"}}, socket}
  end

  # Caller hangs up before the callee answers
  @impl true
  def handle_in("cancel_call", %{"target_user_id" => target_user_id}, socket) do
    caller_id = socket.assigns.user_id

    CallServerWeb.Endpoint.broadcast(
      "user:#{target_user_id}",
      "call_cancelled",
      %{
        caller_id: caller_id
      }
    )

    {:reply, {:ok, %{status: "finished"}}, socket}
  end

  @impl true
  def handle_in("accept_call", payload, socket) do
    caller_id = payload["caller_id"]
    call_id = payload["call_id"] || payload["room_id"]
    room_id = payload["room_id"] || call_id
    Logger.info("Call #{call_id} accepted by user #{socket.assigns.user_id}")

    CallServerWeb.Endpoint.broadcast(
      "user:#{caller_id}",
      "call_accepted",
      %{
        call_id: call_id,
        room_id: room_id,
        callee_id: socket.assigns.user_id
      }
    )

    {:reply, {:ok, %{status: "in_call"}}, socket}
  end
end
