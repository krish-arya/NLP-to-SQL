import React, { useState } from "react";
import { CiMicrophoneOn } from "react-icons/ci";
import { IoSendOutline } from "react-icons/io5";
import { TypeAnimation } from "react-type-animation";

const App = () => {
  const [inputValue, setInputValue] = useState("");
  const [responseData, setResponseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    setLoading(true);
    setError(null);
    setResponseData(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: inputValue }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data = await res.json();
      setResponseData(data);
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
      setInputValue("");
    }
  };

  const handleVoiceInput = () => {
    console.log("Voice input activated");
  };

  return (
    <div className="bg-gray-900 w-full h-screen flex flex-col items-center justify-between py-12">
      <div className="text-center max-w-3xl px-4">
        <h1 className="text-4xl font-bold text-white mb-8">SQL Assistant</h1>
        <TypeAnimation
          sequence={[
            "Converts plain English into SQL queries for easy data access",
            1000,
            "Turns natural language into database commands instantly",
            1000,
            "Bridges human language and SQL for seamless querying",
            1000,
          ]}
          wrapper="span"
          speed={50}
          repeat={Infinity}
          className="text-xl text-gray-400"
        />
      </div>

      <form
        onSubmit={handleSubmit}
        className="border border-gray-700 p-2 rounded-lg w-[80%] max-w-3xl"
      >
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
            disabled={!inputValue.trim() || loading}
          >
            <IoSendOutline className="w-6 h-6 text-gray-400" />
          </button>
        </div>
      </form>

      {/* Display results */}
      <div className="w-[80%] max-w-3xl mt-4 text-left text-gray-300">
        {loading && <p>Loading...</p>}
        {error && <p className="text-red-400">Error: {error}</p>}
        {responseData && (
          <div className="bg-gray-800 p-4 rounded-lg">
            {responseData.agent_output && (
              <p>
                <strong>Agent Output:</strong> {responseData.agent_output}
              </p>
            )}
            {responseData.sql && (
              <p className="mt-2">
                <strong>SQL:</strong> {responseData.sql}
              </p>
            )}
            {responseData.rows && (
              <div className="mt-2">
                <strong>Rows:</strong>
                <pre className="bg-gray-900 p-2 mt-1 rounded">
                  {JSON.stringify(responseData.rows, null, 2)}
                </pre>
              </div>
            )}
            {responseData.error && (
              <p className="text-yellow-400 mt-2">
                Error: {responseData.error}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;