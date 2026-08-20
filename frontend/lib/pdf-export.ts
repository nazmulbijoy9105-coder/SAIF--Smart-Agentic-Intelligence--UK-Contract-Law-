"use client";

// ILRMF v3.0 FIX: Added optional filename parameter to match frontend call
export function exportToPDF(data: any, filename?: string) {
    if (!data) return;

    const facts = data.facts || {};
    const issues = data.issues || [];
    const relief = data.relief || {};
    const governance = data.governance || {};
    const assessmentId = data.assessment_id || "N/A";
    const date = new Date().toLocaleDateString("en-GB", {
        day: "numeric", month: "long", year: "numeric"
    });

    const safeText = (text: any) => {
        if (text === null || text === undefined) return "N/A";
        return String(text);
    };

    const htmlContent = `
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8">
        <style>
            @page { size: A4; margin: 2.5cm 2cm; }
            body { font-family: 'Times New Roman', Times, serif; color: #000; font-size: 12pt; line-height: 1.6; }
            h1, h2, h3, h4 { color: #1a1a1a; font-weight: bold; }
            .header { text-align: center; border-bottom: 3px double #000; padding-bottom: 15px; margin-bottom: 25px; }
            .header h1 { margin: 0; font-size: 22pt; letter-spacing: 1px; }
            .header p { margin: 5px 0 0 0; font-size: 10pt; color: #555; }
            .confidential { text-align: center; font-weight: bold; font-size: 10pt; color: #8b0000; margin-bottom: 20px; letter-spacing: 2px; }
            .section-title { background-color: #f4f4f4; padding: 8px 12px; font-size: 13pt; border-left: 4px solid #333; margin-top: 30px; margin-bottom: 15px; }
            .facts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 30px; margin-bottom: 20px; font-size: 11pt; }
            .label { font-weight: bold; color: #333; }
            .clause-box { background: #f9f9f9; border: 1px solid #ddd; padding: 12px; font-style: italic; font-size: 11pt; margin-bottom: 20px; }
            .issue-container { border: 1px solid #e0e0e0; padding: 20px; margin-bottom: 25px; page-break-inside: avoid; }
            .issue-header { font-size: 13pt; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
            .sub-header { font-size: 11pt; font-weight: bold; color: #444; margin-top: 15px; margin-bottom: 5px; text-transform: uppercase; }
            .law-text { font-size: 11pt; text-align: justify; margin-bottom: 15px; }
            .argument-box { background: #fdfdfd; border-left: 3px solid #999; padding: 10px 15px; margin-bottom: 10px; font-size: 11pt; text-align: justify; }
            .verdict-box { background: #eef5ee; border: 1px solid #b0c9b0; padding: 12px; font-weight: bold; font-size: 11pt; margin-top: 15px; }
            .fjr-note { font-size: 10pt; color: #666; font-style: italic; margin-top: 10px; padding: 8px; background: #fffde7; border-left: 3px solid #fbc02d; }
            .relief-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px; }
            .probability-box { text-align: center; border: 2px solid #333; padding: 15px; margin-top: 20px; background: #fafafa; }
            .probability-score { font-size: 28pt; font-weight: bold; margin: 5px 0; }
            .footer { margin-top: 50px; padding-top: 15px; border-top: 1px solid #ccc; font-size: 9pt; color: #666; text-align: justify; }
            .footer-center { text-align: center; margin-top: 10px; }
        </style></head>
        <body>
            <div class="confidential">PRIVATE AND CONFIDENTIAL</div>
            <div class="header">
                <h1>SAIF LEXQUINTET LEGAL ASSESSMENT</h1>
                <p>ILRMF Engine v3.0 — AI + Rule-Based Hybrid Analysis</p>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 10pt; margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px;">
                <span><strong>Report ID:</strong> ${assessmentId}</span>
                <span><strong>Date:</strong> ${date}</span>
                <span><strong>AI Provider:</strong> ${safeText(governance.aiProvider).toUpperCase()}</span>
            </div>
            <div class="section-title">1. CASE PROFILE & FACTS</div>
            <div class="facts-grid">
                <div><span class="label">Parties:</span> ${safeText(facts.parties)}</div>
                <div><span class="label">Contract Type:</span> ${safeText(facts.contractType)} (${safeText(facts.consumerType)})</div>
                <div><span class="label">Contract Value:</span> ${safeText(facts.value)}</div>
                <div><span class="label">Bargaining Power:</span> ${safeText(facts.bargainingPower)}</div>
                <div><span class="label">Standard Form:</span> ${facts.standardForm ? "Yes" : "No"}</div>
            </div>
            ${facts.summary ? `<p style="text-align: justify;"><span class="label">Summary:</span> ${safeText(facts.summary)}</p>` : ""}
            ${facts.disputedClause ? `<div class="sub-header" style="margin-top:20px;">Disputed Clause Text</div><div class="clause-box">"${safeText(facts.disputedClause)}"</div>` : ""}
            <div class="section-title">2. LEGAL ISSUES & ANALYSIS</div>
            ${issues.map((issue: any, index: number) => {
                const fjr = issue.fjr || {};
                const isFjrNA = fjr.score === null || fjr.score === undefined;
                return `<div class="issue-container">
                    <div class="issue-header"><strong>Issue ${index + 1}:</strong> ${safeText(issue.issue)}</div>
                    <div class="sub-header">Applicable Law & Precedent</div>
                    <div class="law-text">${safeText(issue.law)}</div>
                    <div class="sub-header">Claimant Argument</div>
                    <div class="argument-box">${safeText(issue.argument?.claimant)}</div>
                    <div class="sub-header">Defendant Argument</div>
                    <div class="argument-box">${safeText(issue.argument?.defendant)}</div>
                    <div class="verdict-box">Verdict: ${safeText(issue.verdict)}</div>
                    <div class="fjr-note"><strong>FJR Triple-Gate Status:</strong> 
                        ${isFjrNA ? "N/A — FJR test does not apply. " + safeText(fjr.analysis) : `Overall Score: ${fjr.score}/100. Fair: ${fjr.fairScore}/100. Just: ${fjr.justScore}/100. Reasonable: ${fjr.reasonableScore}/100.<br><br>Analysis: ${safeText(fjr.analysis)}`}
                    </div>
                </div>`;
            }).join("")}
            <div class="section-title">3. RECOMMENDED RELIEF & REMEDIES</div>
            <div class="relief-grid">
                <div class="relief-item"><span class="label">Primary Remedy:</span><br>${safeText(relief.primary)}</div>
                <div class="relief-item"><span class="label">Secondary Remedy:</span><br>${safeText(relief.secondary)}</div>
                <div class="relief-item"><span class="label">Damages / Value:</span><br><strong>${safeText(relief.damages)}</strong></div>
                <div class="relief-item"><span class="label">Designated Forum:</span><br>${safeText(relief.court)}</div>
            </div>
            <div class="probability-box">
                <div style="font-size: 10pt; text-transform: uppercase; letter-spacing: 1px;">Success Probability</div>
                <div class="probability-score">${relief.probability || 0}%</div>
                <div style="font-size: 10pt;">(${safeText(governance.probabilityConfidence)} Confidence)</div>
            </div>
            <div class="section-title">4. GOVERNANCE & AUDIT</div>
            <div style="font-size: 10pt; display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
                <div><strong>Hallucination Check:</strong> <span style="color: ${governance.hallucination === "ZERO" ? "green" : "red"}; font-weight:bold;">${safeText(governance.hallucination)}</span></div>
                <div><strong>Citations Verified:</strong> ${governance.citationValidation?.verified_count || 0} | Flagged: ${governance.citationValidation?.flagged_count || 0}</div>
                <div><strong>Pipeline:</strong> ${safeText(governance.pipeline)}</div>
                <div><strong>GDPR Status:</strong> ${safeText(governance.gdprCompliance) || "Standard Processing"}</div>
            </div>
            <div class="footer">
                <p><strong>Prepared by:</strong> SAIF LexQuintet (ILRMF Engine v3.0) — Creator: Md Nazmul Islam (Bijoy), NB TECH Bangladesh.</p>
                <p><strong>Disclaimer:</strong> This report is generated by an AI-assisted hybrid engine for informational purposes only. It does not constitute formal legal advice. Consult a qualified solicitor regulated by the Solicitors Regulation Authority (SRA) before acting on this information.</p>
                <div class="footer-center">&copy; ${new Date().getFullYear()} NB TECH Bangladesh. All Rights Reserved.</div>
            </div>
        </body></html>
    `;

    const printWindow = window.open("", "_blank");
    if (printWindow) {
        printWindow.document.write(htmlContent);
        printWindow.document.close();
        setTimeout(() => { printWindow.print(); }, 500);
    } else {
        alert("Please allow pop-ups to generate the PDF report.");
    }
}
