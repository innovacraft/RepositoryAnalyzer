import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // Make sure your CSS is properly defined

function App() {
    const [repoUrl, setRepoUrl] = useState('');
    const [token, setToken] = useState('');
    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);

    const fetchFiles = async () => {
        try {
            const response = await axios.get(`/files?repo_url=${encodeURIComponent(repoUrl)}&github_token=${encodeURIComponent(token)}`);
            setFiles(response.data); // Assuming this returns an array of file names or objects
            console.log('Files fetched:', response.data);
        } catch (error) {
            console.error('Failed to fetch files:', error);
        }
    };

    const handleFileSelection = (file) => {
    setSelectedFile(file.url); // Assuming 'file' is an object with a 'url' property
    console.log('File selected:', file.url);
};

    const analyzeFile = async () => {
        if (selectedFile) {
            console.log('Sending for analysis:', selectedFile);
            try {
                const response = await axios.post('/analyze', { content: selectedFile }, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                console.log('Analysis result:', response.data);
            } catch (error) {
                console.error('Error during analysis:', error.response ? error.response.data : error);
            }
        } else {
            console.error('No file selected for analysis');
        }
    };

    return (
        <div className="app">
            <h1>Repository Analyzer</h1>
            <div className="input-group">
                <input
                    type="text"
                    placeholder="Repository URL"
                    value={repoUrl}
                    onChange={e => setRepoUrl(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="GitHub Token (optional)"
                    value={token}
                    onChange={e => setToken(e.target.value)}
                />
                <button onClick={fetchFiles}>Fetch Files</button>
            </div>
            <div className="file-list">
                {files.map((file, index) => (
                    <div key={index} onClick={() => handleFileSelection(file)} className="file-item">
                        {typeof file === 'string' ? file : file.name} // Display file name or adjust as per the structure of file
                    </div>
                ))}
            </div>
            <button onClick={analyzeFile} className="analyze-button">Analyze</button>
        </div>
    );
}

export default App;
