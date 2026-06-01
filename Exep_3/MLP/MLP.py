from __future__ import annotations

import csv
from pathlib import Path

import numpy as np 
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

class PreprocessResult:
    def __init__(
        self,
        train_features: np.ndarray,
        train_target: np.ndarray,
        val_features: np.ndarray,
        val_target: np.ndarray,
        test_features: np.ndarray | None,
        test_ids: np.ndarray | None,
        feature_columns: list[str],
        target_min: float,
        target_max: float,
        numeric_columns: list[str],
    ) -> None:
        self.train_features = train_features
        self.train_target = train_target
        self.val_features = val_features
        self.val_target = val_target
        self.test_features = test_features
        self.test_ids = test_ids
        self.feature_columns = feature_columns
        self.target_min = target_min
        self.target_max = target_max
        self.numeric_columns = numeric_columns


class MLP:
    def __init__(self, input_size: int, hidden_size: int, output_size: int = 1, learning_rate: float = 0.01, seed: int = 42):
        self.input_size = input_size #输入层大小
        self.hidden_size = hidden_size #隐藏层大小
        self.output_size = output_size #输出层大小
        self.learning_rate = learning_rate #学习率
        self.rng = np.random.default_rng(seed) 

        limit_1 = np.sqrt(6.0 / (input_size + hidden_size)) 
        limit_2 = np.sqrt(6.0 / (hidden_size + output_size))
        self.W1 = self.rng.uniform(-limit_1, limit_1, size=(input_size, hidden_size)) 
        self.b1 = np.zeros((1, hidden_size), dtype=np.float64)
        self.W2 = self.rng.uniform(-limit_2, limit_2, size=(hidden_size, output_size))
        self.b2 = np.zeros((1, output_size), dtype=np.float64)

    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        x = np.clip(x, -500, 500) 
        return 1.0 / (1.0 + np.exp(-x))
    
    #sigmoid函数求导
    def d_sigmoid(self, activated: np.ndarray) -> np.ndarray:
        return activated * (1.0 - activated)

    #前向传播
    def forward(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        net = np.dot(x, self.W1) + self.b1 
        activation = self.sigmoid(net) 
        output = np.dot(activation, self.W2) + self.b2
        return activation, output

    #采用MSE作为损失函数
    def loss_MSE(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return float(np.mean((y_true - y_pred) ** 2))

    #反向传播
    def backward(self, x: np.ndarray, y_true: np.ndarray, activation: np.ndarray, y_pred: np.ndarray) -> None:
        batch_size = x.shape[0]  
        error = y_pred - y_true  #输出层误差

        dW2 = np.dot(activation.T, error) / batch_size
        db2 = np.mean(error, axis=0, keepdims=True)

        hidden_error = np.dot(error, self.W2.T) * self.d_sigmoid(activation)   #隐藏层误差
        dW1 = np.dot(x.T, hidden_error) / batch_size   
        db1 = np.mean(hidden_error, axis=0, keepdims=True) 

        #更新参数
        self.W2 -= self.learning_rate * dW2
        self.b2 -= self.learning_rate * db2
        self.W1 -= self.learning_rate * dW1
        self.b1 -= self.learning_rate * db1

    def fit(
        self,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_val: np.ndarray | None = None,
        y_val: np.ndarray | None = None,
        epochs: int = 500, 
        batch_size: int = 32
    ) -> dict[str, list[float]]:
        history = {"train_loss": [], "val_loss": []}  #记录训练和验证损失
        best_val_loss = float("inf") 
        best_state = None
        wait = 0
        patience = 40  #耐心值

        for epoch in range(epochs):
            indices = self.rng.permutation(x_train.shape[0])  
            x_shuffled = x_train[indices]
            y_shuffled = y_train[indices]

            for start in range(0, x_shuffled.shape[0], batch_size):
                end = start + batch_size
                batch_x = x_shuffled[start:end]
                batch_y = y_shuffled[start:end]
                activation, y_pred = self.forward(batch_x)
                self.backward(batch_x, batch_y, activation, y_pred)
            
            train_pred = self.predict(x_train)
            train_loss = self.loss_MSE(y_train, train_pred)
            history["train_loss"].append(train_loss)

            #计算验证损失
            if x_val is not None and y_val is not None:
                val_pred = self.predict(x_val)
                val_loss = self.loss_MSE(y_val, val_pred)
                history["val_loss"].append(val_loss)

                #记录最优验证损失
                if val_loss < best_val_loss - 1e-6:
                    best_val_loss = val_loss
                    best_state = (
                        self.W1.copy(),
                        self.b1.copy(),
                        self.W2.copy(),
                        self.b2.copy(),
                    )
                    wait = 0
                else:
                    wait += 1

                if (epoch + 1) % 20 == 0:
                    print(f"Epoch {epoch + 1} | train_mse={train_loss:.6f} | val_mse={val_loss:.6f}")

                #超过耐心值，提前停止训练
                if wait >= patience:
                    print(f"Early stopping at epoch {epoch + 1}, best_val_mse={best_val_loss:.6f}")
                    break
            else:
                if (epoch + 1) % 20 == 0:
                    print(f"Epoch {epoch + 1} | train_mse={train_loss:.6f}")

        if best_state is not None:
            self.W1, self.b1, self.W2, self.b2 = best_state

        return history

    def predict(self, x: np.ndarray) -> np.ndarray:
        _, y_pred = self.forward(x)
        return y_pred


def read_rows(file_path: Path) -> list[dict[str, str]]:
    with open(file_path, 'r', encoding='utf-8') as file_handle:
        reader = csv.DictReader(file_handle)
        return list(reader)

#字符串转化为浮点数
def str2float(value: str | None) -> float | None:
    try:
        return float(value)  
    except (TypeError, ValueError):
        return None

#建立分类的字典
def build_dict(
    rows: list[dict[str, str]],
    numeric_columns: list[str],
    feature_columns: list[str],
) -> tuple[list[dict[str, float]], np.ndarray | None]:
    feature_dicts: list[dict[str, float]] = []
    test_ids: list[int] | None = [] if any("Id" in row for row in rows) else None

    for row in rows:
        row_features: dict[str, float] = {}

        for column in numeric_columns:
            value = str2float(row.get(column))
            #默认或缺失值为0.0
            row_features[column] = value if value is not None else 0.0

        for column in feature_columns:
            value = row.get(column)
            #默认或缺失值为"Missing"
            if value is None or value == "":
                value = "Missing"
            row_features[f"{column}={value}"] = 1.0

        feature_dicts.append(row_features)

        if test_ids is not None:
            id_value = row.get("Id")
            if id_value is not None and id_value.isdigit():
                test_ids.append(int(id_value))

    return feature_dicts, None if test_ids is None else np.asarray(test_ids, dtype=np.int64)


# 数据加载和预处理
def load_and_preprocess(train_path: Path, test_path: Path | None = None, val_size: float = 0.15, seed: int = 1) -> PreprocessResult:
    train_rows = read_rows(train_path)

    feature_names = [name for name in train_rows[0].keys() if name not in {"SalePrice", "Id"}]   #将SalePrice和Id排除在特征之外
    target = np.asarray([float(row["SalePrice"]) for row in train_rows]).reshape(-1, 1) #把房价提取变为列向量。

    numeric_columns: list[str] = []  #数值列
    feature_columns: list[str] = []  #特征列

    for column in feature_names:
        numeric_values: list[float] = []
        is_numeric = True
        for row in train_rows:
            value = row.get(column)
            parsed_value = str2float(value)
            if parsed_value is None:
                continue
            numeric_values.append(parsed_value)
        for row in train_rows:
            value = row.get(column)
            if value is None or value == "":
                continue
            if str2float(value) is None:
                is_numeric = False
                break
        if is_numeric and numeric_values:
            numeric_columns.append(column)
        else:
            feature_columns.append(column)

    # 丢弃训练集中在任一数值列上缺失的整行（同时确保 SalePrice 可用）
    filtered_train_rows: list[dict[str, str]] = []
    for row in train_rows:
        skip = False
        # 检查数值列
        for col in numeric_columns:
            if str2float(row.get(col)) is None:
                skip = True
                break
        # 检查目标列
        if str2float(row.get("SalePrice")) is None:
            skip = True
        if not skip:
            filtered_train_rows.append(row)

    train_rows = filtered_train_rows

    train_feature_dicts, _ = build_dict(train_rows, numeric_columns, feature_columns)

    vectorizer = DictVectorizer(sparse=False)
    x = vectorizer.fit_transform(train_feature_dicts).astype(np.float64)
    feature_columns = vectorizer.get_feature_names_out().tolist()

    test_features = None
    test_ids = None
    if test_path is not None:
        test_rows = read_rows(test_path)
        # 丢弃测试集中在任一数值列上缺失的整行
        filtered_test_rows: list[dict[str, str]] = []
        for row in test_rows:
            skip = False
            for col in numeric_columns:
                if str2float(row.get(col)) is None:
                    skip = True
                    break
            if not skip:
                filtered_test_rows.append(row)

        test_feature_dicts, test_ids = build_dict(filtered_test_rows, numeric_columns, feature_columns)
        test_features = vectorizer.transform(test_feature_dicts).astype(np.float64)

    x_train, x_val, y_train, y_val = train_test_split(x, target, test_size=val_size, random_state=seed)

    x_mean = x_train.mean(axis=0, keepdims=True)
    x_std = x_train.std(axis=0, keepdims=True)
    x_std[x_std == 0] = 1.0

    x_train = (x_train - x_mean) / x_std
    x_val = (x_val - x_mean) / x_std

    if test_features is not None:
        test_features = (test_features - x_mean) / x_std

    y_min = float(y_train.min())
    y_max = float(y_train.max())
    y_range = y_max - y_min if y_max > y_min else 1.0
    y_train = (y_train - y_min) / y_range
    y_val = (y_val - y_min) / y_range

    return PreprocessResult(
        train_features=x_train,
        train_target=y_train,
        val_features=x_val,
        val_target=y_val,
        test_features=test_features,
        test_ids=test_ids,
        feature_columns=feature_columns,
        target_min=y_min,
        target_max=y_max,
        numeric_columns=numeric_columns,
    )


def inverse_scale_target(values: np.ndarray, target_min: float, target_max: float) -> np.ndarray:
    target_range = target_max - target_min if target_max > target_min else 1.0
    return values * target_range + target_min


def main() -> None:
    train_path = "E:\projects\Python\SYSU_AI\Exep_3\MLP\\train.csv"
    test_path = "E:\projects\Python\SYSU_AI\Exep_3\MLP\\test.csv"

    data = load_and_preprocess(train_path, test_path=test_path)

    model = MLP(
        input_size=data.train_features.shape[1],
        hidden_size=64,
        output_size=1,
        learning_rate=0.01,
        seed=42,
    )

    print(f"Input size: {data.train_features.shape[1]}")
    print("Starting training with sigmoid hidden layer, MSE loss, and random initialization.")
    model.fit(
        data.train_features,
        data.train_target,
        x_val=data.val_features,
        y_val=data.val_target,
        epochs=400,
        batch_size=32,
    )

    val_pred_scaled = model.predict(data.val_features)
    val_pred = inverse_scale_target(val_pred_scaled, data.target_min, data.target_max)
    val_true = inverse_scale_target(data.val_target, data.target_min, data.target_max)
    val_rmse = float(np.sqrt(np.mean((val_pred - val_true) ** 2)))
    print(f"验证集尺度: {val_rmse:.4f}")

    if data.test_features is not None:
        test_pred_scaled = model.predict(data.test_features)
        test_pred = inverse_scale_target(test_pred_scaled, data.target_min, data.target_max).reshape(-1)
        test_pred = np.clip(test_pred, a_min=0.0, a_max=None)

        output_path = "E:\projects\Python\SYSU_AI\Exep_3\MLP\\mlp_predictions.csv"
        with open(output_path, "w", newline="", encoding="utf-8") as file_handle:
            writer = csv.writer(file_handle)
            if data.test_ids is not None:
                writer.writerow(["Id", "SalePrice"])
                for item_id, sale_price in zip(data.test_ids, test_pred):
                    writer.writerow([int(item_id), float(sale_price)])
            else:
                writer.writerow(["SalePrice"])
                for sale_price in test_pred:
                    writer.writerow([float(sale_price)])
        print(f"预测保存至 {output_path}")


if __name__ == "__main__":
    main()