document.addEventListener('DOMContentLoaded', () => {
    const btnRun = document.getElementById('btn-run-ats');
    
    if (btnRun) {
        btnRun.addEventListener('click', async () => {
            const resumeId = document.getElementById('ats-resume-select').value;
            const jobTitle = document.getElementById('ats-job-title').value;
            const jobDescription = document.getElementById('ats-job-desc').value;

            if (!jobDescription) {
                Toast.show('Please provide a job description.', 'danger');
                return;
            }

            btnRun.disabled = true;
            btnRun.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing Match...';

            try {
                const res = await apiRequest('/api/ats/analyze', 'POST', {
                    resume_id: resumeId,
                    job_title: jobTitle,
                    job_description: jobDescription
                });

                if (res.success) {
                    document.getElementById('ats-results').style.display = 'block';
                    document.getElementById('score-display').textContent = `${res.data.score}%`;

                    const matchedList = document.getElementById('matched-keywords-list');
                    const missingList = document.getElementById('missing-keywords-list');

                    matchedList.innerHTML = res.data.matched_keywords.map(k => `<li>${k}</li>`).join('');
                    missingList.innerHTML = res.data.missing_keywords.map(k => `<li>${k}</li>`).join('');

                    Toast.show('Analysis complete!', 'success');
                }
            } catch (err) {
            } finally {
                btnRun.disabled = false;
                btnRun.innerHTML = 'Run Match Analysis';
            }
        });
    }
});