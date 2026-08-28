package ca.utoronto.utm.assignment1.othello;

import java.util.ArrayList;
import java.util.Random;

public class PlayerRandom {
	
	private Random rand = new Random();
	private ArrayList<Move> moves = new ArrayList<>();

	private OthelloBoard board;
	private char player;

	public PlayerRandom(OthelloBoard board, char player) {
		this.board = board;
		this.player = player;
	}

	private void addMove(int row, int col) {
		int[] drow = {0, 1, 0, -1, 1, -1, 1, -1};
		int[] dcol = {1, 0, -1, 0, 1, -1, -1, 1};

		for (int i = 0; i < drow.length; i++) {
			if (board.hasMove(row, col, drow[i], dcol[i]) == player) {
				moves.add(new Move(row, col));
				break;
			}
		}
	}

	private void findMove() {
		moves.clear();

		for (int row = 0; row < board.getDimension(); row++) {
			for (int col = 0; col < board.getDimension(); col++) {
				if (board.get(row, col) == OthelloBoard.EMPTY) {
					addMove(row, col);
				}
			}
		}
	}

	public Move getMove() {
		findMove();

		if (moves.isEmpty()) {
			return null;
		}

		int random = rand.nextInt(moves.size());
		return moves.get(random);
	}
}
