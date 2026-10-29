#!/usr/bin/env python3
"""Рисунки отчёта по фактическим данным northwind_dwh."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

PSQL = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
OUT = Path(__file__).resolve().parents[1] / "report" / "images"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#4C78A8"
ORANGE = "#E07A3D"
GREEN = "#59A14F"
PURPLE = "#B07AA1"
INK = "#1F2A33"
MUTED = "#5C6B76"


def query(sql: str) -> list[list[str]]:
    env = os.environ.copy()
    env["PGPASSWORD"] = "dwh"
    env["PGCLIENTENCODING"] = "UTF8"
    wrapped = f"COPY ({sql}) TO STDOUT WITH CSV"
    completed = subprocess.run(
        [PSQL, "-U", "dwh", "-h", "127.0.0.1", "-d", "northwind_dwh", "-c", wrapped],
        env=env,
        capture_output=True,
        check=True,
    )
    text = completed.stdout.decode("utf-8")
    return [line.split(",") for line in text.splitlines() if line]


def box(ax, x, y, w, h, text, face, edge, fs=9):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=face, edgecolor=edge, linewidth=1.4,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.25)


def arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12, color=MUTED, linewidth=1.2))


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(12.2, 2.4))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 2.4)
    ax.axis("off")
    items = [
        (0.25, "OLTP\nNorthwind, 3НФ", "#D6E6F5", BLUE),
        (2.7, "ETL\npostgres_fdw", "#FDE6D4", ORANGE),
        (5.15, "ХД northwind_dwh\nсхема «звезда»", "#D6E6F5", BLUE),
        (7.7, "Витрина\nv_sales_flat", "#D9EFD4", GREEN),
        (10.05, "SQL-отчёты\nи панели", "#E9DDF0", PURPLE),
    ]
    for x, text, face, edge in items:
        box(ax, x, 0.7, 1.95, 1.15, text, face, edge, fs=9)
    arrow(ax, 2.2, 1.27, 2.7, 1.27)
    arrow(ax, 4.65, 1.27, 5.15, 1.27)
    arrow(ax, 7.1, 1.27, 7.7, 1.27)
    arrow(ax, 9.65, 1.27, 10.05, 1.27)
    ax.text(2.45, 1.55, "SELECT", ha="center", fontsize=8, color=MUTED)
    ax.text(4.9, 1.55, "INSERT", ha="center", fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(OUT / "architecture.png", dpi=140)
    plt.close(fig)


def star() -> None:
    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    box(ax, 3.35, 2.85, 3.3, 1.5, "fact_order_line\nпозиция заказа\nвыручка, скидка, кол-во", "#FDE6D4", ORANGE, fs=10)
    dims = [
        (3.55, 5.55, "dim_date\nдата заказа"),
        (0.35, 3.05, "dim_customer\nклиент, город,\nстрана"),
        (6.85, 3.05, "dim_product\nтовар, категория,\nпоставщик"),
        (0.55, 0.45, "dim_employee\nсотрудник,\nруководитель"),
        (6.85, 0.45, "dim_shipper\nперевозчик"),
    ]
    for x, y, text in dims:
        box(ax, x, y, 2.6, 1.25, text, "#D6E6F5", BLUE, fs=9)
    arrow(ax, 5.0, 4.35, 5.0, 5.55)
    arrow(ax, 3.35, 3.6, 2.95, 3.6)
    arrow(ax, 6.65, 3.6, 6.85, 3.6)
    arrow(ax, 4.2, 2.85, 2.4, 1.7)
    arrow(ax, 5.8, 2.85, 7.6, 1.7)
    fig.tight_layout()
    fig.savefig(OUT / "star_schema.png", dpi=140)
    plt.close(fig)


def style_ax(ax, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    ax.grid(axis="y", color="#E6EBEF", linewidth=0.8)
    ax.set_axisbelow(True)


def dash_sales() -> None:
    quarters = query(
        "SELECT year::text || '-Q' || quarter::text, round(sum(line_total), 2) "
        "FROM v_sales_flat GROUP BY year, quarter ORDER BY year, quarter"
    )
    countries = query(
        "SELECT country, round(sum(line_total), 2) FROM v_sales_flat "
        "GROUP BY country ORDER BY sum(line_total) DESC LIMIT 8"
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    fig.suptitle("Панель «Продажи»", fontsize=13, color=INK, x=0.02, ha="left")
    axes[0].bar([r[0] for r in quarters], [float(r[1]) for r in quarters], color=ORANGE)
    style_ax(axes[0], "Выручка по кварталам")
    axes[0].tick_params(axis="x", rotation=40)
    axes[0].set_ylabel("Выручка")
    countries = list(reversed(countries))
    axes[1].barh([r[0] for r in countries], [float(r[1]) for r in countries], color=BLUE)
    style_ax(axes[1], "Топ-8 стран клиентов")
    axes[1].grid(axis="x", color="#E6EBEF", linewidth=0.8)
    axes[1].grid(axis="y", visible=False)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT / "dash_sales.png", dpi=140)
    plt.close(fig)


def dash_products() -> None:
    cats = query(
        "SELECT category_name, round(sum(line_total), 2) FROM v_sales_flat "
        "GROUP BY category_name ORDER BY sum(line_total) DESC"
    )
    disc = query(
        "SELECT category_name, round(100.0 * sum(discount_amount) "
        "/ nullif(sum(line_total) + sum(discount_amount), 0), 2) "
        "FROM v_sales_flat GROUP BY category_name "
        "ORDER BY 2 DESC"
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    fig.suptitle("Панель «Ассортимент и скидки»", fontsize=13, color=INK, x=0.02, ha="left")
    cats = list(reversed(cats))
    axes[0].barh([r[0] for r in cats], [float(r[1]) for r in cats], color=GREEN)
    style_ax(axes[0], "Выручка по категориям")
    axes[0].grid(axis="x", color="#E6EBEF", linewidth=0.8)
    axes[0].grid(axis="y", visible=False)
    axes[1].bar([r[0] for r in disc], [float(r[1]) for r in disc], color=PURPLE)
    style_ax(axes[1], "Доля скидки, %")
    axes[1].tick_params(axis="x", rotation=35)
    axes[1].set_ylabel("%")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT / "dash_products.png", dpi=140)
    plt.close(fig)


def dash_channel() -> None:
    employees = query(
        "SELECT split_part(employee, ' ', 2), round(sum(line_total), 2) "
        "FROM v_sales_flat GROUP BY employee ORDER BY sum(line_total) DESC"
    )
    shippers = query(
        "SELECT shipper, round(sum(revenue), 2), round(sum(freight), 2) FROM ("
        "  SELECT order_id, shipper, max(order_freight) AS freight, sum(line_total) AS revenue "
        "  FROM v_sales_flat GROUP BY order_id, shipper"
        ") s GROUP BY shipper ORDER BY sum(revenue) DESC"
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6))
    fig.suptitle("Панель «Сотрудники и доставка»", fontsize=13, color=INK, x=0.02, ha="left")
    employees = list(reversed(employees))
    axes[0].barh([r[0] for r in employees], [float(r[1]) for r in employees], color=BLUE)
    style_ax(axes[0], "Выручка по сотрудникам")
    axes[0].grid(axis="x", color="#E6EBEF", linewidth=0.8)
    axes[0].grid(axis="y", visible=False)
    names = [r[0] for r in shippers]
    x = range(len(names))
    axes[1].bar([i - 0.18 for i in x], [float(r[1]) for r in shippers], width=0.36, color=ORANGE, label="Выручка")
    ax2 = axes[1].twinx()
    ax2.bar([i + 0.18 for i in x], [float(r[2]) for r in shippers], width=0.36, color=PURPLE, label="Фрахт")
    style_ax(axes[1], "Перевозчики: выручка и фрахт")
    axes[1].set_xticks(list(x), names, rotation=15)
    axes[1].legend(loc="upper left", fontsize=8, frameon=False)
    ax2.legend(loc="upper right", fontsize=8, frameon=False)
    ax2.spines["top"].set_visible(False)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT / "dash_channel.png", dpi=140)
    plt.close(fig)


def main() -> None:
    architecture()
    star()
    dash_sales()
    dash_products()
    dash_channel()
    print("saved", OUT)


if __name__ == "__main__":
    main()
