import React from "react";
import "./UserTable.css";

const users = [
  {
    id: 1,
    name: "John Smith",
    email: "john@gmail.com",
    role: "Student",
    status: "Active",
  },
  {
    id: 2,
    name: "Sarah Lee",
    email: "sarah@gmail.com",
    role: "Teacher",
    status: "Active",
  },
  {
    id: 3,
    name: "David Wilson",
    email: "david@gmail.com",
    role: "Student",
    status: "Pending",
  },
  {
    id: 4,
    name: "Emily Clark",
    email: "emily@gmail.com",
    role: "Admin",
    status: "Active",
  },
];

const UserTable = () => {
  return (
    <div className="user-table-card">

      <div className="table-header">
        <h2>Latest Users</h2>
        <button>View All</button>
      </div>

      <table>

        <thead>

          <tr>

            <th>Name</th>

            <th>Email</th>

            <th>Role</th>

            <th>Status</th>

          </tr>

        </thead>

        <tbody>

          {users.map((user) => (

            <tr key={user.id}>

              <td>{user.name}</td>

              <td>{user.email}</td>

              <td>{user.role}</td>

              <td>

                <span className={`status ${user.status.toLowerCase()}`}>
                  {user.status}
                </span>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
};

export default UserTable;