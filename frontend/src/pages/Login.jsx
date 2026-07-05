 import React from "react";
import "./Login.css";
import { Link } from "react-router-dom";

const Login = () => {
  return (
    <div className="login-page">

      {/* Left Section */}
      <div className="left-side">

        <div className="logo">
          <div className="logo-icon">🧠</div>

          <div>
            <h2>Smart Quiz</h2>
            <span>Generator</span>
          </div>
        </div>

        <div className="badge">
          ✨ AI-Powered Learning
        </div>

        <h1>
          Welcome Back!
        </h1>

        <p>
          Log in to your account and continue your
          learning journey with AI.
        </p>

        <div className="illustration">

          <div className="card">

            <div className="card-top"></div>

            <div className="card-body">

              <div className="avatar"></div>

              <div className="lines">
                <div></div>
                <div></div>
                <div></div>
              </div>

            </div>

          </div>

          <div className="lock">
            🔒
          </div>

        </div>

        <div className="features">

          <div className="feature">
            <div className="icon">✨</div>
            <h4>AI-Powered</h4>
            <p>Smart quiz generation</p>
          </div>

          <div className="feature">
            <div className="icon">📊</div>
            <h4>Track Progress</h4>
            <p>Monitor and improve</p>
          </div>

          <div className="feature">
            <div className="icon">🎯</div>
            <h4>Achieve Goals</h4>
            <p>Learn, practice and excel</p>
          </div>

        </div>

      </div>

      {/* Right Section */}

      <div className="right-side">

        <div className="login-box">

          <h2>Login to Your Account</h2>

          <p>
            Enter your credentials to access your account
          </p>

          <form>

            <label>Email Address</label>

            <input
              type="email"
              placeholder="Enter your email address"
            />

            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
            />

            <div className="options">

              <label>

                <input type="checkbox" />

                Remember me

              </label>

              <a href="#">
                Forgot Password?
              </a>

            </div>

            <button>

              Login

            </button>

          </form>

          <div className="signup">

            Don't have an account?

            <Link to="/register">

              Sign up

            </Link>

          </div>

        </div>

      </div>

    </div>
  );
};

export default Login;