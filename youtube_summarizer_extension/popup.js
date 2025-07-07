document.addEventListener('DOMContentLoaded', () => {
    const summarizeBtn = document.getElementById('summarizeBtn');
    const resultEl = document.getElementById('result');
    const copyBtn = document.getElementById('copyBtn');

    // Hide Copy button initially
    copyBtn.style.display = "none";

    summarizeBtn.addEventListener('click', () => {
        copyBtn.style.display = "none"; // Hide Copy button before fetching new summary
        resultEl.innerText = "Loading...";

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const url = tabs[0].url;

            fetch('http://127.0.0.1:5000/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            })
            .then(res => res.json())
            .then(data => {
                resultEl.innerText = data.summary || "Error!";
                if (data.summary) {
                    copyBtn.style.display = "block";
                }
            })
            .catch(err => {
                resultEl.innerText = "Error fetching summary!";
                console.log(err);
            });
        });
    });

    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(resultEl.innerText)
            .then(() => alert("Summary copied!"))
            .catch(() => alert("Failed to copy!"));
    });
});
