package ca.utoronto.utm.assignment1.othello;

public class OthelloBoard {
	
	public static final char EMPTY = ' ', P1 = 'X', P2 = 'O', BOTH = 'B';
	private int dim = 8;
	private final char[][] board;
	private boolean multipleFlips = false;

	public OthelloBoard(int dim) {
		this.dim = dim;
		board = new char[this.dim][this.dim];
		for (int row = 0; row < this.dim; row++) {
			for (int col = 0; col < this.dim; col++) {
				this.board[row][col] = EMPTY;
			}
		}
		int mid = this.dim / 2;
		this.board[mid - 1][mid - 1] = this.board[mid][mid] = P1;
		this.board[mid][mid - 1] = this.board[mid - 1][mid] = P2;
	}

	public int getDimension() {
		return this.dim;
	}

	public static char otherPlayer(char player) {
        return switch (player) {
            case P1 -> P2;
            case P2 -> P1;
            case EMPTY -> EMPTY;
            default -> EMPTY;
        };
	}

	public char get(int row, int col) {
		if (0 <= row && row < this.dim && 0 <= col && col < this.dim) {
			if (this.board[row][col] == P1) {
				return P1;
			}
			else if (this.board[row][col] == P2) {
				return P2;
			}
		}
		return EMPTY;
    }

	protected boolean validCoordinate(int row, int col) {
        return 0 <= row && row < this.dim && 0 <= col && col < this.dim;
    }

	protected char alternation(int row, int col, int drow, int dcol) {
		if (this.validCoordinate(row, col)) {
			if ((drow < -1 || drow > 1) || (dcol < -1 || dcol > 1)) {
				return EMPTY;
			}
			char currP = this.board[row][col];
			char otherP;

			if (currP == P1) {
				otherP = P2;
			}
			else if (currP == P2) {
				otherP = P1;
			}
			else {
				return EMPTY;
			}

			while (this.validCoordinate(row, col)) {
				if (this.board[row][col] == EMPTY) {
					return EMPTY;
				}

				else if (otherP == this.board[row][col]) {
					return otherP;
				}
				row += drow;
				col += dcol;
			}
		}
		return EMPTY;
	}

	private int flip(int row, int col, int drow, int dcol, char player) {
		if (this.alternation(row, col, drow, dcol) != player && this.alternation(row, col, drow, dcol) != EMPTY) { // MIKOOO COMMENT --> can store as var, but its still rather meh either way you want to do ti
			int count = 0;

			row += drow;
			col += dcol;

			while (validCoordinate(row, col)) {
				if (this.board[row][col] == player) {
					return count;
				}
				if (this.board[row][col] != EMPTY && this.board[row][col] != player) {
					this.board[row][col] = player;
					count++;
				}
				else {
					return -1;
				}
				row += drow;
				col += dcol;
			}
		}
		return -1;
	}

	protected char hasMove(int row, int col, int drow, int dcol) {
		if (this.validCoordinate(row, col) && (this.board[row][col] == EMPTY || this.multipleFlips)) {

			row += drow;
			col += dcol;

			if (this.validCoordinate(row, col)) {
				char token = this.board[row][col];

				if (token == EMPTY) {
					return EMPTY;
				}

				char othertoken;
				if (token == P1) {
					othertoken = P2;
				}
				else {
					othertoken = P1;
				}

				row += drow;
				col += dcol;

				while (this.validCoordinate(row, col)) {
					if (this.board[row][col] == EMPTY) {
						return EMPTY;
					}
					else if (this.board[row][col] == othertoken) {
						return othertoken;
					}
					row += drow;
					col += dcol;
				}
			}
		}
		return EMPTY;
	}

	public char hasMove() {
		boolean p1move = false;
		boolean p2move = false;

		for (int row = 0; row < this.dim; row++) {
			for (int col = 0; col < this.dim; col++) {

				int[] drow = {0, 1, 0, -1, 1, -1, 1, -1};
				int[] dcol = {1, 0, -1, 0, 1, -1, -1, 1};

				for (int i = 0; i < drow.length; i++) {
					if (this.hasMove(row, col, drow[i], dcol[i]) == P1) {
						p1move = true;
					}
					else if (this.hasMove(row, col, drow[i], dcol[i]) == P2) {
						p2move = true;
					}
					if (p1move && p2move) {
						return BOTH;
					}
				}
			}
		}
		if (p1move) {
			return P1;
		}
		if (p2move) {
			return P2;
		}
		return EMPTY;
    }

	public boolean move(int row, int col, char player) {
		// HINT: Use some of the above helper methods to get this methods
		// job done!!
		if (!this.validCoordinate(row, col) || this.board[row][col] != EMPTY) {
			return false;
		}

		int[] drow = {0, 1, 0, -1, 1, -1, 1, -1};// MIKOOO COMMENT --> my eyes.
		int[] dcol = {1, 0, -1, 0, 1, -1, -1, 1};
		boolean validMove = false;
		int movedTrue = 0;

		for (int i = 0; i < drow.length; i++) {
			if (this.hasMove(row, col, drow[i], dcol[i]) == player) {
				this.board[row][col] = player;
				this.multipleFlips = true;
				if (this.flip(row, col, drow[i], dcol[i], player) > 0) {
					movedTrue += 1;
				}
				if (movedTrue > 0) {
					validMove = true;
				}
			}
		}
		this.multipleFlips = false;
        return validMove;
    }

	public int getCount(char player) {
		int count = 0;
		for (int row = 0; row < this.dim; row++) {
			for (int col = 0; col < this.dim; col++) {
				if (player == P1) {
					if (this.board[row][col] == P1) {
						count++;
					}
				}
				else if (player == P2) {
					if (this.board[row][col] == P2) {
						count++;
					}
				}
			}
		}
		return count;
	}

	public String toString() {
		String s = "";
		s += "  ";
		for (int col = 0; col < this.dim; col++) {
			s += col + " ";
		}
		s += '\n';

		s += " +";
		for (int col = 0; col < this.dim; col++) {
			s += "-+";
		}
		s += '\n';

		for (int row = 0; row < this.dim; row++) {
			s += row + "|";
			for (int col = 0; col < this.dim; col++) {
				s += this.board[row][col] + "|";
			}
			s += row + "\n";

			s += " +";
			for (int col = 0; col < this.dim; col++) {
				s += "-+";
			}
			s += '\n';
		}
		s += "  ";
		for (int col = 0; col < this.dim; col++) {
			s += col + " ";
		}
		s += '\n';
		return s;
	}

	public static void main(String[] args) {
		
		OthelloBoard ob = new OthelloBoard(8);
		System.out.println(ob);
		System.out.println("getCount(P1)=" + ob.getCount(P1));
		System.out.println("getCount(P2)=" + ob.getCount(P2));
		for (int row = 0; row < ob.dim; row++) {
			for (int col = 0; col < ob.dim; col++) {
				ob.board[row][col] = P1;
			}
		}
		System.out.println(ob);
		System.out.println("getCount(P1)=" + ob.getCount(P1));
		System.out.println("getCount(P2)=" + ob.getCount(P2));

		for (int drow = -1; drow <= 1; drow++) {
			for (int dcol = -1; dcol <= 1; dcol++) {
				System.out.println("alternation=" + ob.alternation(4, 4, drow, dcol));
			}
		}

		for (int row = 0; row < ob.dim; row++) {
			for (int col = 0; col < ob.dim; col++) {
				if (row == 0 || col == 0) {
					ob.board[row][col] = P2;
				}
			}
		}
		System.out.println(ob);

		for (int drow = -1; drow <= 1; drow++) {
			for (int dcol = -1; dcol <= 1; dcol++) {
				System.out.println("direction=(" + drow + "," + dcol + ")");
				System.out.println("alternation=" + ob.alternation(4, 4, drow, dcol));
			}
		}

		System.out.println("Trying to move to (4,4) move=" + ob.move(4, 4, P2));

		ob.board[4][4] = EMPTY;
		ob.board[2][4] = EMPTY;

		System.out.println(ob);

		for (int drow = -1; drow <= 1; drow++) {
			for (int dcol = -1; dcol <= 1; dcol++) {
				System.out.println("direction=(" + drow + "," + dcol + ")");
				System.out.println("hasMove at (4,4) in above direction =" + ob.hasMove(4, 4, drow, dcol));
			}
		}
		System.out.println("who has a move=" + ob.hasMove());
		System.out.println("Trying to move to (4,4) move=" + ob.move(4, 4, P2));
		System.out.println(ob);

	}
}
