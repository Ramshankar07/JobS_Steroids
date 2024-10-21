document.addEventListener('DOMContentLoaded', function() {
    const analyzeButton = document.getElementById('analyzeButton');
    const jobDescription = document.getElementById('jobDescription');
    const resumeUpload = document.getElementById('resumeUpload');
    const resultDiv = document.getElementById('result');
  
    analyzeButton.addEventListener('click', function() {
      if (!jobDescription.value || !resumeUpload.files[0]) {
        resultDiv.textContent = 'Please provide both job description and resume.';
        return;
      }
  
      const formData = new FormData();
      formData.append('job_description', JSON.stringify({ content: jobDescription.value }));
      formData.append('resume', resumeUpload.files[0]);
  
      resultDiv.textContent = 'Analyzing...';
  
      fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        resultDiv.innerHTML = `
          <h3>Analysis Result:</h3>
          <p><strong>Cover Letter:</strong> ${data.cover_letter.substring(0, 100)}...</p>
          <p><strong>Skills Gap:</strong> ${data.skills_analysis.chain_based.skills_gap.substring(0, 100)}...</p>
          <p><strong>Hiring Manager Message:</strong> ${data.hiring_manager_message.substring(0, 100)}...</p>
        `;
      })
      .catch(error => {
        resultDiv.textContent = 'Error: ' + error.message;
      });
    });
  });