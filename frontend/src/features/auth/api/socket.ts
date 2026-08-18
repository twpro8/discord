export const connectSocket = () => {
    const socket: WebSocket = new WebSocket(
        "ws://localhost:4000/socket/websocket"
    )

    socket.onopen = () => {
        console.log("CONNECTED")
    }

    socket.onerror = (error) => {
        console.error("ERROR:", error)
    }

    socket.onclose = () => {
        console.log("CLOSED")
    }
}