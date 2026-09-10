class JobStore {
    static key = "djangospice.jobs";

    static load() {
        try {
            const value = localStorage.getItem(this.key);

            if (!value) {
                return new Map();
            }

            const data = JSON.parse(value);

            if (
                !data ||
                typeof data !== "object" ||
                Array.isArray(data)
            ) {
                return new Map();
            }

            return new Map(
                Object.entries(data),
            );
        } catch (error) {
            console.error(
                "Djangospice: failed to load jobs.",
                error,
            );

            return new Map();
        }
    }

    static save(jobs) {
        try {
            localStorage.setItem(
                this.key,
                JSON.stringify(
                    Object.fromEntries(jobs),
                ),
            );
        } catch (error) {
            console.error(
                "Djangospice: failed to save jobs.",
                error,
            );
        }
    }

    static clear() {
        localStorage.removeItem(this.key);
    }
}


export class Job {
    static jobs = JobStore.load();
    static initialized = false;

    static initialize() {
        if (this.initialized) {
            return;
        }

        this.initialized = true;

        document.addEventListener(
            "djangospice:job_queued",
            (event) => {
                this.update(event.detail.job);
            },
        );

        document.addEventListener(
            "djangospice:job_started",
            (event) => {
                this.update(event.detail.job);
            },
        );

        document.addEventListener(
            "djangospice:job_progressed",
            (event) => {
                this.update(event.detail.job);
            },
        );

        document.addEventListener(
            "djangospice:job_completed",
            (event) => {
                this.update(event.detail.job);
            },
        );

        document.addEventListener(
            "djangospice:job_failed",
            (event) => {
                this.update(event.detail.job);
            },
        );
    }

    static update(job) {
        if (!job?.id) {
            return null;
        }

        const current = this.jobs.get(job.id);

        const updated = {
            ...current,
            ...job,
        };

        this.jobs.set(
            job.id,
            updated,
        );

        JobStore.save(this.jobs);

        return updated;
    }

    static get(id) {
        return this.jobs.get(id);
    }

    static all() {
        return Array.from(
            this.jobs.values(),
        );
    }

    static remove(id) {
        this.jobs.delete(id);

        JobStore.save(this.jobs);
    }

    static clear() {
        this.jobs.clear();
        JobStore.clear();
    }
    
    static has(id) {
        return this.jobs.has(id);
    }
}