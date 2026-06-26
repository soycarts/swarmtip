import React from 'react';

export default function AudioPlayer() {
  return (
    <div className="panel">
      <h2>
        Audio Briefing
        <span className="tag done" style={{ fontSize: '10px' }}>ElevenLabs</span>
      </h2>
      
      <audio controls style={{ width: '100%', height: '36px', marginTop: '8px' }}>
        <source src="data:audio/mp3;base64,//NExAAAAANIAAAAAExBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq" type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>
    </div>
  );
}
