import React, { useState, useEffect, useRef } from 'react';
import './App.css'; // Import Flat UI CSS

const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [text, setText] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [inputText, setInputText] = useState('');
  const [recognition, setRecognition] = useState(null);
  const [recognitionStarted, setRecognitionStarted] = useState(false);
  const textareaRef = useRef(null); // To reference the textarea
  const pressSound = useRef(new Audio('./sounds/press.mp3')); // Path to press sound
  const releaseSound = useRef(new Audio('./sounds/release.mp3')); // Path to release sound

  useEffect(() => {
    // Initialize Speech Recognition API
    if ('webkitSpeechRecognition' in window) {
      const recognitionInstance = new window.webkitSpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setText(transcript); // Update text in real-time
        setInputText(transcript); // Update textarea in real-time
      };
      recognitionInstance.onend = () => {
        setRecognitionStarted(false);
        setIsRecording(false);
      };
      setRecognition(recognitionInstance);
    } else {
      console.error('Speech Recognition API is not supported in this browser.');
    }
  }, []);

  const handleMouseDown = () => {
    if (recognition && !recognitionStarted) {
      try {
        recognition.start();
        setIsRecording(true);
        setRecognitionStarted(true);
        pressSound.current.play(); // Play press sound
      } catch (error) {
        console.error('Error starting recognition:', error);
        stopRecognition();
      }
    }
  };

  const handleMouseUp = () => {
    stopRecognition();
  };

  const stopRecognition = () => {
    if (recognitionStarted) {
      try {
        recognition.stop();
        setIsRecording(false);
        setRecognitionStarted(false);
        setText(''); // Clear the real-time text
        releaseSound.current.play(); // Play release sound
      } catch (error) {
        console.error('Error stopping recognition:', error);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Prevent the default new line
      if (inputText.trim()) {
        setChatHistory([...chatHistory, { user: inputText, system: '...' }]); // Add chat history
        setInputText(''); // Clear the textarea after sending
        // Play sound on send
        const sendSound = new Audio('./sounds/send.mp3');
        sendSound.play();
      }
    }
  };

  return (
    <div className="App">
      <div className={`textarea-container ${isRecording ? 'recording' : ''}`}>
        <div
          className={`microphone-icon ${isRecording ? 'active' : ''}`}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={stopRecognition} // Stop if mouse leaves
        >
          🎤︎
        </div>
        <div className="textarea-wrapper">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            className="textarea"
          />
          <button
            className="send-button"
            onClick={() => {
              if (inputText.trim()) {
                setChatHistory([...chatHistory, { user: inputText, system: '...' }]); // Add chat history
                setInputText(''); // Clear the textarea after sending
                // Play sound on send
                const sendSound = new Audio('./sounds/send.mp3');
                sendSound.play();
              }
            }}
          >
            Send
          </button>
        </div>
      </div>
      <div className="chat-history">
        {chatHistory.map((entry, index) => (
          <div key={index} className="chat-entry">
            <div className="user-message">You: {entry.user}</div>
            <div className="system-message">System: {entry.system}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;
