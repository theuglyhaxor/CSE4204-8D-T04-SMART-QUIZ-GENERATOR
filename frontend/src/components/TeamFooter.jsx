import { useEffect, useState } from "react";
import { meta } from "../api/client";
import "./TeamFooter.css";

/**
 * Team identity footer — the on-screen counterpart of the footer stamped onto every
 * exported quiz PDF. Both read from the same source (settings.TEAM via GET /api/meta/),
 * so the identity is never duplicated or allowed to drift.
 */
export default function TeamFooter({ compact = false }) {
  const [team, setTeam] = useState(null);

  useEffect(() => {
    let cancelled = false;
    meta
      .team()
      .then((data) => !cancelled && setTeam(data))
      .catch(() => {
        /* the footer is decoration — never block the page on it */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!team) return null;

  if (compact) {
    return (
      <footer className="team-footer team-footer--compact">
        <span className="team-footer__id">{team.team_id}</span>
        <span className="team-footer__sep">·</span>
        <span>{team.project}</span>
        <span className="team-footer__sep">·</span>
        <span>{team.course}</span>
      </footer>
    );
  }

  return (
    <footer className="team-footer">
      <div className="team-footer__top">
        <div>
          <div className="team-footer__id">{team.team_id}</div>
          <div className="team-footer__project">{team.project}</div>
        </div>
        <div className="team-footer__org">
          <div>{team.course}</div>
          <div>{team.department}</div>
          <div>{team.university}</div>
        </div>
      </div>

      <ul className="team-footer__members">
        {team.members.map((member) => (
          <li key={member.student_id}>
            <span className="team-footer__name">{member.name}</span>
            <span className="team-footer__sid">{member.student_id}</span>
            <span className="team-footer__role">{member.role}</span>
          </li>
        ))}
      </ul>
    </footer>
  );
}
