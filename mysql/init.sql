-- 檢查是否存在 'accounting' 用戶，若不存在則創建
CREATE USER IF NOT EXISTS 'accounting'@'%' IDENTIFIED BY 'accounting';

-- 授予 'accounting' 用戶對 'accounting' 數據庫的所有權限
GRANT ALL PRIVILEGES ON `accounting`.* TO 'accounting'@'%';

-- 授予 'accounting' 用戶對任何以 'test_' 開頭的數據庫的所有權限（用於 Django 測試數據庫）
GRANT ALL PRIVILEGES ON `test_%`.* TO 'accounting'@'%';

-- 刷新權限以確保更改立即生效
FLUSH PRIVILEGES;
