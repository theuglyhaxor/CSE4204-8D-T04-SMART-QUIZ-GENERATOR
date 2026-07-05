import React from "react";
import "./Register.css";

const Register = () => {
  return (
    <div className="register-container">

      {/* Left Side */}
      <div className="left-panel">
        <div className="logo">
          <span className="logo-icon">★</span>
          <h2>SMART QUIZ</h2>
        </div>

        <div className="welcome-content">
          <h1>Welcome Back!</h1>

          <p>
            Create an account to generate AI powered quizzes,
            manage exams and track your progress easily.
          </p>

          <div className="circle circle1"></div>
          <div className="circle circle2"></div>
          <div className="circle circle3"></div>
        </div>
      </div>

      {/* Right Side */}
      <div className="right-panel">

        <div className="form-box">

          <h2>Create Account</h2>

          <p className="subtitle">
            Please fill the information below.
          </p>

          <form>

            <div className="input-group">
              <label>Full Name</label>
              <input
                type="text"
                placeholder="Enter your full name"
              />
            </div>

            <div className="input-group">
              <label>Email</label>
              <input
                type="email"
                placeholder="Enter your email"
              />
            </div>

            <div className="input-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Password"
              />
            </div>

            <div className="input-group">
              <label>Confirm Password</label>
              <input
                type="password"
                placeholder="Confirm Password"
              />
            </div>

            <button className="register-btn">
              Create Account
            </button>

            <p className="login-text">
              Already have an account?
              <span> Login</span>
            </p>

          </form>

        </div>

      </div>

    </div>
  );
};

export default Register;