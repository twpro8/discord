defmodule CallServerWeb.UserChannel do
  use Phoenix.Channel

  require Logger

  @impl true
  def join("user:" <> user_id, _params, socket) do
    Logger.info("User #{user_id} joined their channel")

    {:ok, socket |> assign(:user_id, user_id)}
  end

  # A calls B
  @impl true
  def handle_in(
        "call_user",
        %{"target_user_id" => target_user_id},
        socket
      ) do
    caller_id = socket.assigns.user_id

    Logger.info("User #{caller_id} wants to call #{target_user_id}")

    call_id = UUID.uuid4()

    # TODO: Validate with Lumiere API

    CallServerWeb.Endpoint.broadcast(
      "user:#{target_user_id}",
      "incoming_call",
      %{
        caller_id: caller_id,
        call_id: call_id
      }
    )

    {:reply,
     {:ok,
      %{
        status: "ringing",
        call_id: call_id
      }}, socket}
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
  def handle_in("accept_call", %{"caller_id" => caller_id, "call_id" => call_id}, socket) do
    Logger.info("Call #{call_id} accepted by user #{socket.assigns.user_id}")

    CallServerWeb.Endpoint.broadcast(
      "user:#{caller_id}",
      "call_accepted",
      %{
        call_id: call_id,
        callee_id: socket.assigns.user_id
      }
    )

    {:reply, {:ok, %{status: "in_call"}}, socket}
  end
end
