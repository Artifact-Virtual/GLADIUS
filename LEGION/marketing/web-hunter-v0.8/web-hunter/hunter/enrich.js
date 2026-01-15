const fs = require('fs');
const path = require('path');

// Load leads data
const leadsFilePath = path.join(__dirname, '../data/leads.json');
let leads = JSON.parse(fs.readFileSync(leadsFilePath, 'utf8'));

// Function to enrich leads
function enrichLeads() {
    return leads.map(lead => {
        // Example enrichment logic
        lead.enriched = true; // Mark lead as enriched
        lead.score = Math.random() * 100; // Assign a random score
        return lead;
    });
}

// Save enriched leads to file
function saveEnrichedLeads(enrichedLeads) {
    const enrichedFilePath = path.join(__dirname, '../data/enriched.json');
    fs.writeFileSync(enrichedFilePath, JSON.stringify(enrichedLeads, null, 2));
}

// Main function to run enrichment process
function runEnrichment() {
    const enrichedLeads = enrichLeads();
    saveEnrichedLeads(enrichedLeads);
}

// Export the enrichment functions
module.exports = {
    enrichLeads,
    saveEnrichedLeads,
    runEnrichment
};