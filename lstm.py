import torch
from torch import nn

class LSTM(nn.Module):
	def __init__(self, input_size=1, hidden_layer_size=50, output_size=1):
		super().__init__()
		self.hidden_layer_size = hidden_layer_size

		self.lstm = nn.LSTM(input_size, hidden_layer_size)

		self.linear = nn.Linear(hidden_layer_size, output_size)

		self.hidden_cell = (torch.zeros(1,1,self.hidden_layer_size),
							torch.zeros(1,1,self.hidden_layer_size))

	def forward(self, input_seq):
		lstm_out, self.hidden_cell = self.lstm(input_seq.view(len(input_seq) ,1, -1), self.hidden_cell)
		predictions = self.linear(lstm_out.view(len(input_seq), -1))
		return predictions[-1]
		
model = LSTM()
loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)	
print(model)

epochs = 150

for i in range(epochs):
	for seq, labels in train_inout_seq:
		optimizer.zero_grad()
		model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
						torch.zeros(1, 1, model.hidden_layer_size))

		y_pred = model(seq)

		single_loss = loss_function(y_pred, labels)
		single_loss.backward()
		optimizer.step()

	if i%25 == 1:
		print(f'epoch: {i:3} loss: {single_loss.item():10.8f}')

print(f'epoch: {i:3} loss: {single_loss.item():10.10f}')