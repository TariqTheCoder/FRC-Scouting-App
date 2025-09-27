INSERT INTO match_scouting (
  match_number, team_number, scouter_name, starting_pos,
  l1_auto, l2_auto, l3_auto, l4_auto, algae_auto,
  l1, l2, l3, l4, algae,
  intake_missed, scorer_missed,
  defense_method, defense_amount, penalty_amount,
  endgame_type, failed_endgame, is_disabled, tipped
) VALUES (
  %(match_number)s, %(team_number)s, %(scouter_name)s, %(starting_pos)s,
  %(l1_auto)s, %(l2_auto)s, %(l3_auto)s, %(l4_auto)s, %(algae_auto)s,
  %(l1)s, %(l2)s, %(l3)s, %(l4)s, %(algae)s,
  %(intake_missed)s, %(scorer_missed)s,
  %(defense_method)s, %(defense_amount)s, %(penalty_amount)s,
  %(endgame_type)s, %(failed_endgame)s, %(is_disabled)s, %(tipped)s
);