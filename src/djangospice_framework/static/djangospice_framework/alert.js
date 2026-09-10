export class Alert {
    static renderers = new Map();
    static initialized = false;

    static initialize() {
        if (this.initialized) {
            return;
        }

        this.initialized = true;

        document.addEventListener(
            "djangospice:alert",
            (event) => {
                this.dispatch(event.detail);
            },
        );
    }

    static register(name, renderer) {
        if (!name) {
            throw new Error(
                "Djangospice: alert renderer name is required.",
            );
        }

        if (
            !renderer ||
            typeof renderer.render !== "function"
        ) {
            throw new TypeError(
                "Djangospice: alert renderer must implement render().",
            );
        }

        this.renderers.set(name, renderer);

        return renderer;
    }

    static unregister(name) {
        return this.renderers.delete(name);
    }

    static get(name) {
        return this.renderers.get(name);
    }

    static dispatch(event) {
        if (!event) {
            return;
        }

        const alert = event.alert;

        if (!alert) {
            return;
        }

        const rendererName = alert.renderer;

        if (!rendererName) {
            return;
        }

        const renderer = this.get(rendererName);

        if (!renderer) {
            console.warn(
                `Djangospice: alert renderer "${rendererName}" is not registered.`,
            );

            return;
        }

        renderer.render(alert, event);
    }

    static clear() {
        this.renderers.clear();
    }
}