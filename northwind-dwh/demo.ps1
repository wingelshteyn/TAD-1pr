$Host.UI.RawUI.WindowTitle = "Northwind DWH"
$env:PGPASSWORD = "dwh"
$env:PGCLIENTENCODING = "UTF8"
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
Write-Host "База northwind_dwh, пользователь dwh" -ForegroundColor Cyan
& $psql -U dwh -h 127.0.0.1 -d northwind_dwh -c "SELECT (SELECT count(*) FROM fact_order_line) AS fact_rows, (SELECT round(sum(line_total),2) FROM fact_order_line) AS revenue, (SELECT count(DISTINCT order_id) FROM fact_order_line) AS orders;"
Write-Host ""
Write-Host "Интерактивный psql. Примеры:" -ForegroundColor Cyan
Write-Host "  SELECT * FROM v_sales_flat LIMIT 5;"
Write-Host "  \dt"
Write-Host "  \q  — выход"
Write-Host ""
& $psql -U dwh -h 127.0.0.1 -d northwind_dwh
