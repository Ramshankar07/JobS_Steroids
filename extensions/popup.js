document.addEventListener('DOMContentLoaded', function() {
  const analyzeButton = document.getElementById('analyzeButton');
  const jobDescription = document.getElementById('jobDescription');
  const resumeUpload = document.getElementById('resumeUpload');
  const resultDiv = document.getElementById('result');

  // Add loading state handling
  function setLoading(isLoading) {
    analyzeButton.disabled = isLoading;
    analyzeButton.textContent = isLoading ? 'Analyzing...' : 'Analyze';
    if (isLoading) {
      resultDiv.innerHTML = '<p>Processing your request...</p>';
    }
  }

  // Handle errors
  function showError(message) {
    resultDiv.innerHTML = `
      <div style="color: red; padding: 10px; margin-top: 10px;">
        Error: ${message}
      </div>
    `;
  }

  // Display results
  function showResults(data) {
    resultDiv.innerHTML = `
      <div style="margin-top: 10px;">
        <h3>Analysis Results:</h3>
        
        <div style="margin-bottom: 15px;">
          <h4>Cover Letter Preview:</h4>
          <p>${data.cover_letter.substring(0, 150)}...</p>
          <button onclick="navigator.clipboard.writeText('${data.cover_letter.replace(/'/g, "\\'")}')">
            Copy Full Cover Letter
          </button>
        </div>

        <div style="margin-bottom: 15px;">
          <h4>Skills Analysis:</h4>
          <p><strong>Skills Gap:</strong> ${data.skills_analysis.chain_based.skills_gap}</p>
          <p><strong>Relevant Skills:</strong> ${data.skills_analysis.chain_based.relevant_skills}</p>
        </div>

        <div style="margin-bottom: 15px;">
          <h4>Message to Hiring Manager:</h4>
          <p>${data.hiring_manager_message}</p>
          <button onclick="navigator.clipboard.writeText('${data.hiring_manager_message.replace(/'/g, "\\'")}')">
            Copy Message
          </button>
        </div>
      </div>
    `;
  }

  analyzeButton.addEventListener('click', async function() {
    try {
      if (!jobDescription.value || !resumeUpload.files[0]) {
        showError('Please provide both job description and resume.');
        return;
      }

      setLoading(true);

      const formData = new FormData();
      formData.append('job_description', JSON.stringify({ content: jobDescription.value }));
      formData.append('resume', resumeUpload.files[0]);

      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze job application');
      }

      const data = await response.json();
      showResults(data);
    } catch (error) {
      showError(error.message || 'Failed to connect to the server');
    } finally {
      setLoading(false);
    }
  });
});