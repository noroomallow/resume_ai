document.addEventListener('DOMContentLoaded', () => {
    // Dynamic Application State
    const state = {
        id: document.getElementById('resume-id').value || null,
        experience: [],
        projects: [],
        education: [],
        skills: []
    };

    // DOM Binding elements
    const inputs = {
        fullname: document.getElementById('input-fullname'),
        title: document.getElementById('input-prof-title'),
        email: document.getElementById('input-email'),
        phone: document.getElementById('input-phone'),
        location: document.getElementById('input-location'),
        summary: document.getElementById('input-summary')
    };

    const canvas = {
        name: document.getElementById('cv-name'),
        title: document.getElementById('cv-title'),
        email: document.getElementById('cv-email'),
        phone: document.getElementById('cv-phone'),
        location: document.getElementById('cv-location'),
        summary: document.getElementById('cv-summary-body'),
        expList: document.getElementById('cv-experience-list'),
        projList: document.getElementById('cv-projects-list'),
        eduList: document.getElementById('cv-education-list'),
        skillsList: document.getElementById('cv-skills-list')
    };

    // Initialize State from server payload (if editing existing resume)
    if (window.INITIAL_RESUME_DATA) {
        const d = window.INITIAL_RESUME_DATA;
        state.experience = d.experience || [];
        state.projects = d.projects || [];
        state.education = d.education || [];
        state.skills = d.skills || [];
    }

    // 1. Live Bindings for Basic Information
    Object.keys(inputs).forEach(key => {
        if (inputs[key]) {
            inputs[key].addEventListener('input', () => updateHeaderCanvas());
        }
    });

    function updateHeaderCanvas() {
        canvas.name.textContent = inputs.fullname.value || 'Your Full Name';
        canvas.title.textContent = inputs.title.value || 'Professional Title';
        canvas.email.innerHTML = `<i class="fas fa-envelope"></i> ${inputs.email.value || 'email@example.com'}`;
        canvas.phone.innerHTML = `<i class="fas fa-phone"></i> ${inputs.phone.value || '+1 (555) 000-0000'}`;
        canvas.location.innerHTML = `<i class="fas fa-map-marker-alt"></i> ${inputs.location.value || 'City, Country'}`;
        canvas.summary.textContent = inputs.summary.value || 'Summary highlights will render here...';
    }

    // 2. Dynamic Experience Handler
    const expContainer = document.getElementById('experience-list-container');
    document.getElementById('btn-add-experience').addEventListener('click', () => {
        state.experience.push({ company: '', position: '', start_date: '', end_date: '', description: '' });
        renderExperienceForms();
        renderExperienceCanvas();
    });

    function renderExperienceForms() {
        expContainer.innerHTML = '';
        state.experience.forEach((exp, index) => {
            const card = document.createElement('div');
            card.className = 'dynamic-card';
            card.innerHTML = `
                <button type="button" class="remove-btn" onclick="removeExperience(${index})"><i class="fas fa-trash"></i></button>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" value="${exp.company || ''}" oninput="updateExpField(${index}, 'company', this.value)">
                    </div>
                    <div class="form-group">
                        <label>Position</label>
                        <input type="text" value="${exp.position || ''}" oninput="updateExpField(${index}, 'position', this.value)">
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="text" placeholder="e.g. Jan 2022" value="${exp.start_date || ''}" oninput="updateExpField(${index}, 'start_date', this.value)">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="text" placeholder="e.g. Present" value="${exp.end_date || ''}" oninput="updateExpField(${index}, 'end_date', this.value)">
                    </div>
                    <div class="form-group full-width">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <label>Description</label>
                            <button type="button" class="btn-ai-btn" onclick="triggerAiExperience(${index})"><i class="fas fa-magic"></i> Improve</button>
                        </div>
                        <textarea rows="3" oninput="updateExpField(${index}, 'description', this.value)">${exp.description || ''}</textarea>
                    </div>
                </div>
            `;
            expContainer.appendChild(card);
        });
    }

    window.updateExpField = (index, field, val) => {
        state.experience[index][field] = val;
        renderExperienceCanvas();
    };

    window.removeExperience = (index) => {
        state.experience.splice(index, 1);
        renderExperienceForms();
        renderExperienceCanvas();
    };

    function renderExperienceCanvas() {
        canvas.expList.innerHTML = state.experience.map(exp => `
            <div class="cv-item">
                <div class="cv-item-header">
                    <span>${exp.position || 'Position Title'}</span>
                    <span>${exp.start_date || ''} - ${exp.end_date || ''}</span>
                </div>
                <div class="cv-item-sub">${exp.company || 'Company Name'}</div>
                <div class="cv-item-desc">${exp.description || ''}</div>
            </div>
        `).join('');
    }

    // 3. Dynamic Projects Handler
    const projContainer = document.getElementById('project-list-container');
    document.getElementById('btn-add-project').addEventListener('click', () => {
        state.projects.push({ name: '', technologies: '', description: '', github_url: '', live_url: '' });
        renderProjectForms();
        renderProjectCanvas();
    });

    function renderProjectForms() {
        projContainer.innerHTML = '';
        state.projects.forEach((proj, index) => {
            const card = document.createElement('div');
            card.className = 'dynamic-card';
            card.innerHTML = `
                <button type="button" class="remove-btn" onclick="removeProject(${index})"><i class="fas fa-trash"></i></button>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Project Name</label>
                        <input type="text" value="${proj.name || ''}" oninput="updateProjField(${index}, 'name', this.value)">
                    </div>
                    <div class="form-group">
                        <label>Technologies Used</label>
                        <input type="text" placeholder="Python, Flask, SQLite" value="${proj.technologies || ''}" oninput="updateProjField(${index}, 'technologies', this.value)">
                    </div>
                    <div class="form-group full-width">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <label>Description</label>
                            <button type="button" class="btn-ai-btn" onclick="triggerAiProject(${index})"><i class="fas fa-magic"></i> Improve</button>
                        </div>
                        <textarea rows="3" oninput="updateProjField(${index}, 'description', this.value)">${proj.description || ''}</textarea>
                    </div>
                </div>
            `;
            projContainer.appendChild(card);
        });
    }

    window.updateProjField = (index, field, val) => {
        state.projects[index][field] = val;
        renderProjectCanvas();
    };

    window.removeProject = (index) => {
        state.projects.splice(index, 1);
        renderProjectForms();
        renderProjectCanvas();
    };

    function renderProjectCanvas() {
        canvas.projList.innerHTML = state.projects.map(p => `
            <div class="cv-item">
                <div class="cv-item-header">
                    <span>${p.name || 'Project Name'}</span>
                </div>
                <div class="cv-item-sub">${p.technologies || ''}</div>
                <div class="cv-item-desc">${p.description || ''}</div>
            </div>
        `).join('');
    }

    // 4. Dynamic Education Handler
    const eduContainer = document.getElementById('education-list-container');
    document.getElementById('btn-add-education').addEventListener('click', () => {
        state.education.push({ degree: '', institution: '', start_date: '', end_date: '' });
        renderEducationForms();
        renderEducationCanvas();
    });

    function renderEducationForms() {
        eduContainer.innerHTML = '';
        state.education.forEach((edu, index) => {
            const card = document.createElement('div');
            card.className = 'dynamic-card';
            card.innerHTML = `
                <button type="button" class="remove-btn" onclick="removeEducation(${index})"><i class="fas fa-trash"></i></button>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Degree / Certificate</label>
                        <input type="text" value="${edu.degree || ''}" oninput="updateEduField(${index}, 'degree', this.value)">
                    </div>
                    <div class="form-group">
                        <label>Institution</label>
                        <input type="text" value="${edu.institution || ''}" oninput="updateEduField(${index}, 'institution', this.value)">
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="text" value="${edu.start_date || ''}" oninput="updateEduField(${index}, 'start_date', this.value)">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="text" value="${edu.end_date || ''}" oninput="updateEduField(${index}, 'end_date', this.value)">
                    </div>
                </div>
            `;
            eduContainer.appendChild(card);
        });
    }

    window.updateEduField = (index, field, val) => {
        state.education[index][field] = val;
        renderEducationCanvas();
    };

    window.removeEducation = (index) => {
        state.education.splice(index, 1);
        renderEducationForms();
        renderEducationCanvas();
    };

    function renderEducationCanvas() {
        canvas.eduList.innerHTML = state.education.map(e => `
            <div class="cv-item">
                <div class="cv-item-header">
                    <span>${e.degree || 'Degree Program'}</span>
                    <span>${e.start_date || ''} - ${e.end_date || ''}</span>
                </div>
                <div class="cv-item-sub">${e.institution || 'University Name'}</div>
            </div>
        `).join('');
    }

    // 5. Dynamic Skills Chip Handler
    const skillContainer = document.getElementById('skill-list-container');
    document.getElementById('btn-add-skill').addEventListener('click', () => {
        const val = prompt('Enter Technical or Soft Skill:');
        if (val && val.trim()) {
            state.skills.push({ skill_name: val.trim(), category: 'Technical' });
            renderSkillChips();
            renderSkillCanvas();
        }
    });

    function renderSkillChips() {
        skillContainer.innerHTML = state.skills.map((s, idx) => `
            <div class="skill-chip">
                <span>${s.skill_name}</span>
                <span onclick="removeSkill(${idx})">&times;</span>
            </div>
        `).join('');
    }

    window.removeSkill = (idx) => {
        state.skills.splice(idx, 1);
        renderSkillChips();
        renderSkillCanvas();
    };

    function renderSkillCanvas() {
        canvas.skillsList.innerHTML = state.skills.map(s => `
            <span class="cv-skill-tag">${s.skill_name}</span>
        `).join('');
    }

    // 6. AI Interactivity Functions
    window.triggerAiProject = async (index) => {
        const item = state.projects[index];
        try {
            const res = await apiRequest('/api/ai/project', 'POST', item);
            if (res.success) {
                state.projects[index].description = res.data;
                renderProjectForms();
                renderProjectCanvas();
                Toast.show('Project description enhanced!', 'success');
            }
        } catch (e) {}
    };

    window.triggerAiExperience = async (index) => {
        const item = state.experience[index];
        try {
            const res = await apiRequest('/api/ai/experience', 'POST', item);
            if (res.success) {
                state.experience[index].description = res.data;
                renderExperienceForms();
                renderExperienceCanvas();
                Toast.show('Work experience updated!', 'success');
            }
        } catch (e) {}
    };

    // Save Complete Form Handler
    document.getElementById('btn-submit-resume').addEventListener('click', async () => {
        const payload = {
            id: document.getElementById('resume-id').value || null,
            title: inputs.title.value,
            full_name: inputs.fullname.value,
            professional_title: inputs.title.value,
            email: inputs.email.value,
            phone: inputs.phone.value,
            location: inputs.location.value,
            summary: inputs.summary.value,
            experience: state.experience,
            projects: state.projects,
            education: state.education,
            skills: state.skills
        };

        try {
            const res = await apiRequest('/api/resume', 'POST', payload);
            if (res.success) {
                document.getElementById('resume-id').value = res.resume_id;
                Toast.show('Resume successfully saved!', 'success');
            }
        } catch (err) {}
    });

    // Initial Dynamic Render Execution
    renderExperienceForms();
    renderExperienceCanvas();
    renderProjectForms();
    renderProjectCanvas();
    renderEducationForms();
    renderEducationCanvas();
    renderSkillChips();
    renderSkillCanvas();
    updateHeaderCanvas();
});