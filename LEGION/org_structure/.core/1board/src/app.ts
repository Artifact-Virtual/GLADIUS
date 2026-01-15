import { WorkspaceManager } from './services/workspace-manager';
import { TemplateGenerator } from './services/template-generator';
import { StrategicOversight } from './templates/strategic-oversight';
import { OperationalOversight } from './templates/operational-oversight';
import { TacticalOversight } from './templates/tactical-oversight';

const workspaceManager = new WorkspaceManager();
const templateGenerator = new TemplateGenerator();

const strategicOversight = new StrategicOversight();
const operationalOversight = new OperationalOversight();
const tacticalOversight = new TacticalOversight();

// Initialize the workspace with oversight layers
workspaceManager.addLayer(strategicOversight);
workspaceManager.addLayer(operationalOversight);
workspaceManager.addLayer(tacticalOversight);

// Generate templates for each oversight layer
const strategicTemplate = templateGenerator.generateTemplate(strategicOversight);
const operationalTemplate = templateGenerator.generateTemplate(operationalOversight);
const tacticalTemplate = templateGenerator.generateTemplate(tacticalOversight);

// Log the generated templates
console.log('Strategic Template:', strategicTemplate);
console.log('Operational Template:', operationalTemplate);
console.log('Tactical Template:', tacticalTemplate);