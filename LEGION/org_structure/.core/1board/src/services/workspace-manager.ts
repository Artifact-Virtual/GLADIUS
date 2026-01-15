export class WorkspaceManager {
    private layers: string[] = [];
    private templates: string[] = [];

    constructor() {}

    addLayer(layer: string): void {
        this.layers.push(layer);
    }

    removeLayer(layer: string): void {
        this.layers = this.layers.filter(existingLayer => existingLayer !== layer);
    }

    addTemplate(template: string): void {
        this.templates.push(template);
    }

    removeTemplate(template: string): void {
        this.templates = this.templates.filter(existingTemplate => existingTemplate !== template);
    }

    getLayers(): string[] {
        return this.layers;
    }

    getTemplates(): string[] {
        return this.templates;
    }
}