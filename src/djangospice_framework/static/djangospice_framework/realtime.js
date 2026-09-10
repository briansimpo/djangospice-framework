/**
 * Djangospice realtime client.
 *
 * The server event name is preserved exactly.
 *
 * Server:
 *
 *     {
 *         "type": "job_progressed",
 *         ...
 *     }
 *
 * Browser:
 *
 *     djangospice:job_progressed
 */
export class Realtime {
    constructor(url, options = {}) {
        this.url = url;

        this.options = {
            reconnect: true,
            reconnectDelay: 3000,
            maxReconnectDelay: 30000,
            ...options,
        };

        this.socket = null;
        this.reconnectTimer = null;
        this.reconnectDelay = this.options.reconnectDelay;
        this.connected = false;
    }

    connect() {
        if (
            this.socket &&
            (
                this.socket.readyState === WebSocket.OPEN ||
                this.socket.readyState === WebSocket.CONNECTING
            )
        ) {
            return;
        }

        this.socket = new WebSocket(this.url);

        this.socket.addEventListener("open", (event) => {
            this.connected = true;
            this.reconnectDelay = this.options.reconnectDelay;

            this.emit("open", event);
        });

        this.socket.addEventListener("message", (event) => {
            this.receive(event.data);
        });

        this.socket.addEventListener("close", (event) => {
            this.connected = false;

            this.emit("close", event);

            if (this.options.reconnect) {
                this.scheduleReconnect();
            }
        });

        this.socket.addEventListener("error", (event) => {
            this.emit("error", event);
        });
    }

    disconnect() {
        this.options.reconnect = false;

        this.clearReconnect();

        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }

        this.connected = false;
    }

    send(data) {
        if (!this.socket) {
            throw new Error(
                "Djangospice realtime connection is not initialized.",
            );
        }

        if (this.socket.readyState !== WebSocket.OPEN) {
            throw new Error(
                "Djangospice realtime connection is not open.",
            );
        }

        this.socket.send(
            typeof data === "string"
                ? data
                : JSON.stringify(data),
        );
    }

    receive(data) {
        let event;

        try {
            event = JSON.parse(data);
        } catch (error) {
            console.error(
                "Djangospice: invalid realtime message.",
                error,
            );

            return;
        }

        if (
            !event ||
            typeof event !== "object" ||
            !event.type
        ) {
            return;
        }

        this.dispatch(event);
    }

    dispatch(event) {
        document.dispatchEvent(
            new CustomEvent(
                `djangospice:${event.type}`,
                {
                    detail: event,
                },
            ),
        );
    }

    emit(type, detail = null) {
        document.dispatchEvent(
            new CustomEvent(
                `djangospice:realtime:${type}`,
                {
                    detail,
                },
            ),
        );
    }

    scheduleReconnect() {
        if (this.reconnectTimer) {
            return;
        }

        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;

            if (!this.options.reconnect) {
                return;
            }

            this.connect();

            this.reconnectDelay = Math.min(
                this.reconnectDelay * 2,
                this.options.maxReconnectDelay,
            );
        }, this.reconnectDelay);
    }

    clearReconnect() {
        if (!this.reconnectTimer) {
            return;
        }

        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
    }
}