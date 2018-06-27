import chess.variant
import torch
import numpy as np
import torch.nn as nn
import torch.utils.data as data_utils
from ChessConvNet import ChessConvNet
import ActionToArray


class ChessEnvironment():

    def __init__(self):
        self.board = chess.variant.CrazyhouseBoard()  # this allows legal moves and all
        self.arrayBoard = [["r", "n", "b", "q", "k", "b", "n", "r"],
                           ["p", "p", "p", "p", "p", "p", "p", "p"],
                           [" ", " ", " ", " ", " ", " ", " ", " "],
                           [" ", " ", " ", " ", " ", " ", " ", " "],
                           [" ", " ", " ", " ", " ", " ", " ", " "],
                           [" ", " ", " ", " ", " ", " ", " ", " "],
                           ["P", "P", "P", "P", "P", "P", "P", "P"],
                           ["R", "N", "B", "Q", "K", "B", "N", "R"]]
        self.actuallyAPawn = np.zeros((8, 8))
        self.plies = 0
        # pawn, knight, bishop, rook, queen.
        self.whiteCaptivePieces = [0, 0, 0, 0, 0]
        self.blackCaptivePieces = [0, 0, 0, 0, 0]

        # This is required
        self.wPawnBoard = np.zeros((8, 8))
        self.bPawnBoard = np.zeros((8, 8))
        self.wKnightBoard = np.zeros((8, 8))
        self.bKnightBoard = np.zeros((8, 8))
        self.wBishopBoard = np.zeros((8, 8))
        self.bBishopBoard = np.zeros((8, 8))
        self.wRookBoard = np.zeros((8, 8))
        self.bRookBoard = np.zeros((8, 8))
        self.wQueenBoard = np.zeros((8, 8))
        self.bQueenBoard = np.zeros((8, 8))
        self.wKingBoard = np.zeros((8, 8))
        self.bKingBoard = np.zeros((8, 8))
        self.allBoards = np.zeros((1, 1))  # this will be refreshed anyway
        self.result = 2  # 2 denotes ongoing, 0 denotes draw, 1 denotes white win, -1 denotes black win
        self.stateFEN = chess.STARTING_FEN  # FEN of starting position
        self.gameStatus = "Game is in progress."

    def boardToFEN(self):
        self.stateFEN = self.board.fen()
        return self.stateFEN

    def boardToString(self):
        state = "0000000000000000000000000000000000000000000000000000000000000000"
        for i in range(8):
            for j in range(8):
                if self.arrayBoard[i][j] != " ":
                    direc = i * 8 + j
                    # change something
                    state = state[0:direc] + self.arrayBoard[i][j] + state[direc + 1:]
        captive = str(self.whiteCaptivePieces[0]) + str(self.whiteCaptivePieces[1]) \
                  + str(self.whiteCaptivePieces[2]) + str(self.whiteCaptivePieces[3]) \
                  + str(self.whiteCaptivePieces[4]) + str(self.blackCaptivePieces[0]) \
                  + str(self.blackCaptivePieces[1]) + str(self.blackCaptivePieces[2]) \
                  + str(self.blackCaptivePieces[3]) + str(self.blackCaptivePieces[4])

        turn = str(self.plies % 2)

        castling = '0000'
        if self.board.has_kingside_castling_rights(chess.WHITE):
            castling = '1000'
        if self.board.has_queenside_castling_rights(chess.WHITE):
            castling = castling[0] + '100'
        if self.board.has_kingside_castling_rights(chess.BLACK):
            castling = castling[0:2] + '10'
        if self.board.has_queenside_castling_rights(chess.BLACK):
            castling = castling[0:3] + '1'
        return state + captive + castling + turn

    def gameResult(self):
        if self.board.is_insufficient_material():
            self.result = 0
            self.gameStatus = "Draw."
        if self.board.is_stalemate():
            self.result = 0
            self.gameStatus = "Draw."
        if self.board.can_claim_draw():
            self.result = 0
            self.gameStatus = "Draw."
        if self.board.is_checkmate():
            if self.plies % 2 == 0:
                # last move was black, therefore black won.
                self.result = -1
                self.gameStatus = "Black Victory"
            if self.plies % 2 == 1:
                self.result = 1
                self.gameStatus = "White Victory"

    def updateNumpyBoards(self):

        # Before updating states, one must refresh the boards.
        self.wPawnBoard = np.zeros((8, 8))
        self.bPawnBoard = np.zeros((8, 8))
        self.wKnightBoard = np.zeros((8, 8))
        self.bKnightBoard = np.zeros((8, 8))
        self.wBishopBoard = np.zeros((8, 8))
        self.bBishopBoard = np.zeros((8, 8))
        self.wRookBoard = np.zeros((8, 8))
        self.bRookBoard = np.zeros((8, 8))
        self.wQueenBoard = np.zeros((8, 8))
        self.bQueenBoard = np.zeros((8, 8))
        self.wKingBoard = np.zeros((8, 8))
        self.bKingBoard = np.zeros((8, 8))

        for i in range(8):
            for j in range(8):
                if self.arrayBoard[i][j] == "P":
                    self.wPawnBoard[i][j] = 1
                if self.arrayBoard[i][j] == "p":
                    self.bPawnBoard[i][j] = 1
                if self.arrayBoard[i][j] == "N":
                    self.wKnightBoard[i][j] = 1
                if self.arrayBoard[i][j] == "n":
                    self.bKnightBoard[i][j] = 1
                if self.arrayBoard[i][j] == "B":
                    self.wBishopBoard[i][j] = 1
                if self.arrayBoard[i][j] == "b":
                    self.bBishopBoard[i][j] = 1
                if self.arrayBoard[i][j] == "R":
                    self.wRookBoard[i][j] = 1
                if self.arrayBoard[i][j] == "r":
                    self.bRookBoard[i][j] = 1
                if self.arrayBoard[i][j] == "Q":
                    self.wQueenBoard[i][j] = 1
                if self.arrayBoard[i][j] == "q":
                    self.bQueenBoard[i][j] = 1
                if self.arrayBoard[i][j] == "K":
                    self.wKingBoard[i][j] = 1
                if self.arrayBoard[i][j] == "k":
                    self.bKingBoard[i][j] = 1
                # once all boards are done, concatenate them into the state
                self.allBoards = np.concatenate((self.wPawnBoard, self.wKnightBoard, self.wBishopBoard, self.wRookBoard,
                                                 self.wQueenBoard, self.wKingBoard,
                                                 self.bPawnBoard, self.bKnightBoard, self.bBishopBoard, self.bRookBoard,
                                                 self.bQueenBoard, self.bKingBoard
                                                 ))

    def makeMove(self, move):
        if chess.Move.from_uci(move) in self.board.legal_moves:
            self.board.push(chess.Move.from_uci(move))
            # update numpy board too - split the move and find coordinates! see old chess java work.
            rowNames = "abcdefgh"
            if move[1] != "@":
                initialRow = 8 - int(move[1])  # for e2d4, move[1] returns 2
            else:
                initialRow = 0
            initialCol = int(rowNames.find(move[0]))  # for e2d4, move[1] returns e
            finalRow = 8 - int(move[3])  # for e2d4, move[3] returns 4
            finalCol = int(rowNames.find(move[2]))  # for e2d4, move[2] returns d
            # SPECIAL MOVE 1: CASTLING
            if move == "e1g1":
                self.arrayBoard[7][4] = " "
                self.arrayBoard[7][7] = " "
                self.arrayBoard[7][5] = "R"
                self.arrayBoard[7][6] = "K"
            elif move == "e8g8":
                self.arrayBoard[0][4] = " "
                self.arrayBoard[0][7] = " "
                self.arrayBoard[0][5] = "R"
                self.arrayBoard[0][6] = "K"
            elif move == "e8c8":
                self.arrayBoard[0][0] = " "
                self.arrayBoard[0][1] = " "
                self.arrayBoard[0][4] = " "
                self.arrayBoard[0][2] = "K"
                self.arrayBoard[0][3] = "R"
            elif move == "e1c1":
                self.arrayBoard[7][0] = " "
                self.arrayBoard[7][1] = " "
                self.arrayBoard[7][4] = " "
                self.arrayBoard[7][2] = "K"
                self.arrayBoard[7][3] = "R"
            # SPECIAL MOVE 2: EN PASSANT
            # check if the capture square is empty and there is a pawn on the same row but different column
            # white en passant
            elif self.arrayBoard[initialRow][initialCol] == "P" and self.arrayBoard[initialRow][finalCol] == "p" and \
                    self.arrayBoard[finalRow][finalCol] == " ":
                # print("WHITE EN PASSANT")
                self.arrayBoard[initialRow][initialCol] = " "
                self.arrayBoard[finalRow][finalCol] = "P"
                self.arrayBoard[initialRow][finalCol] = " "
                self.whiteCaptivePieces[0] += 1
            # black en passant
            elif self.arrayBoard[initialRow][initialCol] == "p" and self.arrayBoard[initialRow][finalCol] == "P" and \
                    self.arrayBoard[finalRow][finalCol] == " ":
                # print("BLACK EN PASSANT")
                self.arrayBoard[initialRow][initialCol] = " "
                self.arrayBoard[finalRow][finalCol] = "p"
                self.arrayBoard[initialRow][finalCol] = " "
                self.blackCaptivePieces[0] += 1
            elif "PRNBQ".find(move[0]) == -1:
                # update the board
                temp = self.arrayBoard[finalRow][finalCol]
                self.arrayBoard[finalRow][finalCol] = self.arrayBoard[initialRow][initialCol]
                self.arrayBoard[initialRow][initialCol] = " "

                # move around the actuallyAPawn stuff too.
                wasAPawn = self.actuallyAPawn[finalRow][finalCol]
                self.actuallyAPawn[finalRow][finalCol] = self.actuallyAPawn[initialRow][initialCol]
                self.actuallyAPawn[initialRow][initialCol] = 0

                # this is for promotion
                if len(move) == 5:
                    if self.plies % 2 == 0:
                        self.arrayBoard[finalRow][finalCol] = move[4].upper()
                    if self.plies % 2 == 1:
                        self.arrayBoard[finalRow][finalCol] = move[4].lower()
                    self.actuallyAPawn[finalRow][finalCol] = 1

                # add pieces to captured area
                if wasAPawn == 0:  # 0 means it is normal.
                    whiteCaptured = "pnbrq".find(temp)
                    blackCaptured = "PNBRQ".find(temp)
                    if whiteCaptured > -1:
                        self.whiteCaptivePieces[whiteCaptured] += 1
                    if blackCaptured > -1:
                        self.blackCaptivePieces[blackCaptured] += 1
                if wasAPawn == 1:  # 1 means that the piece in question was once a pawn.
                    if self.plies % 2 == 0:
                        self.whiteCaptivePieces[0] += 1
                    if self.plies % 2 == 1:
                        self.blackCaptivePieces[0] += 1

            else:
                # this is when a captured piece is put back on the board

                # update the captive pieces
                placed = "PNBRQ".find(move[0])
                if self.plies % 2 == 0:
                    self.whiteCaptivePieces[placed] -= 1
                if self.plies % 2 == 1:
                    self.blackCaptivePieces[placed] -= 1

                # update the board.
                rowNames = "abcdefgh"
                placedRow = 8 - int(move[3])
                placedCol = int(rowNames.find(move[2]))

                if self.plies % 2 == 0:
                    self.arrayBoard[placedRow][placedCol] = move[0]
                if self.plies % 2 == 1:
                    self.arrayBoard[placedRow][placedCol] = move[0].lower()

            # once everything is done, update move count
            self.updateNumpyBoards()
            self.plies += 1
        else:
            print(move)
            print("Illegal Move!")

    def printBoard(self):
        print(self.board)
        print(self.arrayBoard)
        print(self.whiteCaptivePieces)
        print(self.blackCaptivePieces)

    def boardToState(self):

        captiveToBinary = np.zeros((8, 8))

        # Create copies of whiteCaptive and blackCaptive
        temp1 = np.copy(self.whiteCaptivePieces)
        temp2 = np.copy(self.blackCaptivePieces)

        # start off by updating pawns.
        for i in range(8):
            if temp1[0] > 0:
                captiveToBinary[0][i] = 1
                temp1[0] -= 1
            if temp2[0] > 0:
                captiveToBinary[4][i] = 1
                temp2[0] -= 1
        for i in range(8):
            if temp1[0] > 0:
                captiveToBinary[1][i] = 1
                temp1[0] -= 1
            if temp2[0] > 0:
                captiveToBinary[5][i] = 1
                temp2[0] -= 1

        # then, update knights, bishops, and rooks, and then queen.
        for i in range(4):
            if temp1[1] > 0:
                captiveToBinary[2][i] = 1
                temp1[1] -= 1
            if temp1[2] > 0:
                captiveToBinary[2][4 + i] = 1
                temp1[2] -= 1
            if temp1[3] > 0:
                captiveToBinary[3][i] = 1
                temp1[3] -= 1
            if temp1[4] > 0:
                captiveToBinary[3][4 + i] = 1
                temp1[4] -= 1
            if temp2[1] > 0:
                captiveToBinary[6][i] = 1
                temp2[1] -= 1
            if temp2[2] > 0:
                captiveToBinary[6][4 + i] = 1
                temp2[2] -= 1
            if temp2[3] > 0:
                captiveToBinary[7][i] = 1
                temp2[3] -= 1
            if temp2[4] > 0:
                captiveToBinary[7][4 + i] = 1
                temp2[4] -= 1

            # [7][6], [7][7] determine who is moving
            captiveToBinary[7][6], captiveToBinary[7][7] = (self.plies % 2), (self.plies % 2)

            # need four more entries to determine who can castle...
            # [3][6], [3][7]
            # captiveToBinary[3][6] = self.board.castling_rights

        self.updateNumpyBoards()

        # perhaps work on adding 1s for spaces....
        return np.reshape(np.concatenate((self.allBoards, captiveToBinary)), (1, 1, 104, 8))  # 32, 26, or 104, 8


board = ChessEnvironment()

# here is a fascinating crazyhouse game...
listOfMoves = ["e2e4", "e7e6", "d2d4", "b8c6", "g1f3", "d7d5", "e4e5", "g8e7", "b1c3", "e7f5", "f1d3", "c6d4",
               "f3d4", "f5d4", "e1g1", "d4f5", "d3f5", "e6f5", "c3d5", "B@e4", "d5e3", "P@h3", "d1d8", "e8d8",
               "f1d1", "c8d7", "d1d7", "d8d7", "Q@d4", "R@d6", "N@c5", "d7e8", "B@b5", "c7c6", "e5d6", "h3g2",
               "N@c7", "e8d8", "R@e8"]

inputs = np.zeros(1)
outputs = np.zeros(1)

for i in range(len(listOfMoves)):
    state = board.boardToState()
    action = ActionToArray.moveArray(listOfMoves[i], board.arrayBoard)
    print(ActionToArray.moveArrayToString(action, board.arrayBoard, board.board,
                                          board.whiteCaptivePieces, board.blackCaptivePieces,
                                          board.plies))

    print(board.boardToString())
    print(board.boardToFEN())
    print(board.board)
    if board.board.legal_moves.count() != len(ActionToArray.legalMovesForState(board.arrayBoard, board.board)):
        print("ERROR!")

    board.makeMove(listOfMoves[i])
    if i == 0:
        inputs = state
        outputs = action
    else:
        inputs = np.concatenate((inputs, state))
        outputs = np.concatenate((outputs, action))

print("FINAL POSITION:")
print(board.board)
print(board.boardToString())
board.gameResult()
print(board.gameStatus)

# TIME FOR THE ML WORK

# Hyper Parameters
EPOCHS = 1000  # train the training data n times, to save time, we just train 1 epoch
BATCH_SIZE = 1000  # batch size
LR = 0.001  # learning rate
OUTPUT_ARRAY_LEN = 4504  # actual length of array output

inputs = torch.from_numpy(inputs)
outputs = torch.from_numpy(outputs)

boards, actions = inputs, outputs


class MyDataset(torch.utils.data.Dataset):

    def __init__(self, inputs, outputs):
        self.features = inputs
        self.targets = outputs

    def __getitem__(self, index):
        return self.features[index], self.targets[index]

    def __len__(self):
        return len(self.features)


data = MyDataset(boards, actions)

trainLoader = torch.utils.data.DataLoader(dataset=data, batch_size=BATCH_SIZE, shuffle=True)
testLoader = torch.utils.data.DataLoader(dataset=data, batch_size=len(boards), shuffle=False)
# to create a prediction, create a new dataset with input of the states, and output should just be np.zeros()

# TRAINING!
model = ChessConvNet(OUTPUT_ARRAY_LEN).double()

criterion = nn.PoissonNLLLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

total_step = len(trainLoader)

train = True
if train:
    for epoch in range(EPOCHS):
        for i, (images, labels) in enumerate(trainLoader):
            images = images.to('cpu')
            labels = labels.to('cpu')

            # print(images.shape)

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (i + 1) % 1 == 0:
                print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                      .format(epoch + 1, EPOCHS, i + 1, total_step, loss.item()))

            # Test the model
            model.eval()  # eval mode (batchnorm uses moving mean/variance instead of mini-batch mean/variance)
            answers = np.argmax(actions.numpy(), axis=1)
            with torch.no_grad():
                for images, labels in testLoader:
                    images = images.to('cpu')
                    labels = labels.to('cpu')
                    outputs = model(images)
                    _, predicted = torch.max(outputs.data, 1)

                    # print expectations vs reality
                    print("Predicted:")
                    print(predicted.numpy())
                    print("Actual:")
                    print(answers)

                    correct = (predicted.numpy() == answers).sum()
                    accuracy = 100 * (correct / len(answers))

                    if epoch % 50 == 1:
                        newBoard = ChessEnvironment()
                        for i in range(len(outputs.numpy())):
                            if newBoard.result == 2:
                                move = ActionToArray.moveArrayToString(outputs.numpy()[i].reshape((1, 4504)),
                                                                   newBoard.arrayBoard, newBoard.board,
                                                                   newBoard.whiteCaptivePieces, newBoard.blackCaptivePieces,
                                                                   newBoard.plies)
                                print(move)
                                legalMoves = ActionToArray.legalMovesForState(newBoard.arrayBoard, newBoard.board)
                                evaluationScores = ActionToArray.moveEvaluations(
                                    ActionToArray.legalMovesForState(newBoard.arrayBoard, newBoard.board), newBoard.arrayBoard,
                                    outputs[i])
                                print("Evaluation Rankings: ")
                                print(" = " + legalMoves[np.argmax(evaluationScores)])
                                print(ActionToArray.sortEvals(legalMoves, evaluationScores))

                                newBoard.makeMove(move)
                                newBoard.gameResult()
                            else:
                                print(newBoard.gameStatus)

                        print(newBoard.board)
                        newBoard.gameResult()
                        print(newBoard.boardToString())
                        print(newBoard.gameStatus)

                    print(accuracy, "% correct.")
