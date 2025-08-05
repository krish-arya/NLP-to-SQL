import React, { useState } from "react";
import { CiMicrophoneOn } from "react-icons/ci";
import { IoSendOutline } from "react-icons/io5";
import { TypeAnimation } from 'react-type-animation';

const App = () => {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle submission logic here
    console.log("Submitted:", inputValue);
    setInputValue("");
  };

  const handleVoiceInput = () => {
    // Voice input logic would go here
    console.log("Voice input activated");
  };

  return (
    <div className="bg-gray-900 w-full h-screen flex flex-col items-center justify-between py-12">
      <div className="text-center max-w-3xl px-4">
        <h1 className="text-4xl font-bold text-white mb-8">SQL Assistant</h1>
        <TypeAnimation
          sequence={[
            'Converts plain English into SQL queries for easy data access',
            1000,
            'Turns natural language into database commands instantly',
            1000,
            'Bridges human language and SQL for seamless querying',
            1000
          ]}
          wrapper="span"
          speed={50}
          repeat={Infinity}
          className="text-xl text-gray-400"
        />
      </div>
      
      <form onSubmit={handleSubmit} className="border border-gray-700 p-2 rounded-lg w-[80%] max-w-3xl">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Type your message here..."
            className="w-full bg-transparent text-gray-400 border-none outline-none"
          />
          <button 
            type="button"
            onClick={handleVoiceInput}
            className="p-2 hover:bg-gray-800 rounded-full transition-colors"
          >
            <CiMicrophoneOn className="w-6 h-6 text-gray-400" />
          </button>
          <button 
            type="submit"
            className="p-2 hover:bg-gray-800 rounded-full transition-colors"
            disabled={!inputValue.trim()}
          >
            <IoSendOutline className="w-6 h-6 text-gray-400" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default App;