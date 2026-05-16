export function exportToPDF(data: any) {
    const lines = ['SAIF Assessment Report', `ID: ${data.assessment_id || 'N/A'}`, '---', 'ISSUES:', ...(data.issues || []).map((i: any, idx: number) => `${idx+1}. ${i.issue} | FJR: ${i.fjr?.score}/100 | Verdict: ${i.verdict}`)];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `SAIF-${data.assessment_id||'report'}.txt`; a.click();
}
