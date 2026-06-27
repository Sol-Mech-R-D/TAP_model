# -*- coding: utf-8 -*-
"""
generate_excel.py
=================
Generates a beautifully styled Excel workbook (assets/tap_model_comprehensive_report.xlsx) 
containing all 99 objections tribunal checks, equations, expected vs calculated values, 
and the global parameter sweep data.
"""

import os
import sys
import json
import math
import numpy as np
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Ensure src/ is in the python path
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from update_readme_full import get_math_formula
from tap_parameter_sweep import solve_cascade_errors
from science_constants import PHI

def main():
    print("=" * 80)
    print("  TAP COMPREHENSIVE EXCEL EXPORTER")
    print("  Generating publication-grade Excel report...")
    print("=" * 80)

    # 1. Load results JSON
    json_path = os.path.join(src_dir, "tap_super_tribunal_99_results.json")
    if not os.path.exists(json_path):
        print(f"  [ERROR] Results JSON not found at {json_path}. Run tap_super_tribunal_99.py first.")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    # Create Workbook
    wb = openpyxl.Workbook()
    
    # Setup styles
    font_family = "Segoe UI"
    title_font = Font(name=font_family, size=16, bold=True, color="FFFFFF")
    header_font = Font(name=font_family, size=11, bold=True, color="FFFFFF")
    bold_font = Font(name=font_family, size=11, bold=True)
    normal_font = Font(name=font_family, size=10)
    italic_font = Font(name=font_family, size=10, italic=True)
    
    # Colors (Elegant Slate/Navy theme)
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    accent_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
    zebra_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    pass_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    pass_font = Font(name=font_family, size=10, color="006100")
    
    thin_border_side = Side(border_style="thin", color="D9D9D9")
    thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    thick_bottom = Border(bottom=Side(border_style="medium", color="1F4E78"))
    double_bottom = Border(bottom=Side(border_style="double", color="1F4E78"), top=Side(border_style="thin", color="D9D9D9"))

    # =========================================================================
    # TAB 1: OVERVIEW
    # =========================================================================
    ws_ov = wb.active
    ws_ov.title = "TAP Model Overview"
    ws_ov.views.sheetView[0].showGridLines = True
    
    # Title Block
    ws_ov.merge_cells("A1:D2")
    title_cell = ws_ov["A1"]
    title_cell.value = "Topological Action Physics (TAP) Model Overview"
    title_cell.font = title_font
    title_cell.fill = header_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    overview_data = [
        ("Parameter", "Symbol / Equation", "Value", "Description"),
        ("Golden Ratio (Base Parameter)", "phi", PHI, "Fundamental geometric scale factor of the 13D compactified flavor manifold."),
        ("Bulk Dimension", "D", 13.0, "Total number of dimensions in topological saturation limit."),
        ("Planck Mass Scale", "m_P", "1.2209e19 GeV", "Fundamental cutoff energy scale of the bulk manifold."),
        ("Electroweak VEV", "v", "246.22 GeV", "Dynamic vacuum expectation value resolved by Dirac Sturm-Liouville spectrum."),
        ("Higgs Mass Scale", "m_H", "125.09 GeV", "Higgs mass eigenvalue stabilized dynamically at v/2."),
        ("Alpha Inverse (EM Coupling)", "alpha^-1", "4 * pi * phi^5", "Bare electromagnetic coupling strength at Planck boundary."),
        ("Weak Mixing Angle", "sin^2(theta_W)", "phi^-2", "Bare Weinberg angle predicted at boundary unification scale.")
    ]
    
    row_idx = 4
    for idx, row in enumerate(overview_data):
        for col_idx, val in enumerate(row):
            cell = ws_ov.cell(row=row_idx, column=col_idx+1, value=val)
            if idx == 0:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.font = normal_font
                cell.border = thin_border
                if col_idx == 2 and isinstance(val, (int, float)):
                    cell.number_format = "0.00000"
                if idx % 2 == 1:
                    cell.fill = zebra_fill
        row_idx += 1

    # =========================================================================
    # TAB 2: 99 OBJECTIONS
    # =========================================================================
    ws_checks = wb.create_sheet(title="99 Objections Tribunal")
    ws_checks.views.sheetView[0].showGridLines = True
    ws_checks.freeze_panes = "A2"
    
    headers = [
        "ID", "Category", "Critic", "Objection / Test Name", 
        "Theoretical Formula (LaTeX)", "Standard Lib Value (Path 1)", 
        "TAP Resolved Value (Path 2)", "Relative Error (%)", "Unit", "Status"
    ]
    
    # Write Headers
    for col_idx, h in enumerate(headers):
        cell = ws_checks.cell(row=1, column=col_idx+1, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws_checks.row_dimensions[1].height = 28
    
    # Write Data
    for idx, r in enumerate(results):
        row_num = idx + 2
        formula = get_math_formula(r["id"])
        
        ws_checks.cell(row=row_num, column=1, value=r["id"]).alignment = Alignment(horizontal="center")
        ws_checks.cell(row=row_num, column=2, value=r["category"]).alignment = Alignment(horizontal="left")
        ws_checks.cell(row=row_num, column=3, value=r["critic"]).alignment = Alignment(horizontal="left")
        ws_checks.cell(row=row_num, column=4, value=r["objection"]).alignment = Alignment(horizontal="left")
        
        f_cell = ws_checks.cell(row=row_num, column=5, value=formula)
        f_cell.font = italic_font
        f_cell.alignment = Alignment(horizontal="left")
        
        c_std = ws_checks.cell(row=row_num, column=6, value=r["expected"])
        c_std.number_format = "0.000000E+00" if abs(r["expected"]) < 1e-3 or abs(r["expected"]) > 1e5 else "0.00000"
        
        c_tap = ws_checks.cell(row=row_num, column=7, value=r["value"])
        c_tap.number_format = "0.000000E+00" if abs(r["value"]) < 1e-3 or abs(r["value"]) > 1e5 else "0.00000"
        
        c_err = ws_checks.cell(row=row_num, column=8, value=r["err_pct"] / 100.0)
        c_err.number_format = "0.00%"
        
        unit = ws_checks.cell(row=row_num, column=9, value=r["unit"] if "unit" in r else "dimensionless")
        unit.alignment = Alignment(horizontal="center")
        
        status_cell = ws_checks.cell(row=row_num, column=10, value=r["status"])
        status_cell.font = pass_font
        status_cell.fill = pass_fill
        status_cell.alignment = Alignment(horizontal="center")
        
        # Apply normal formatting & border to row
        for c in range(1, 11):
            cell = ws_checks.cell(row=row_num, column=c)
            if c != 10:  # Status has its own styling
                cell.font = normal_font
                if idx % 2 == 1:
                    cell.fill = zebra_fill
            cell.border = thin_border
            
    # Add Summary Row
    summary_row = len(results) + 2
    ws_checks.cell(row=summary_row, column=3, value="Total Passed:").font = bold_font
    ws_checks.cell(row=summary_row, column=3).alignment = Alignment(horizontal="right")
    
    passed_cell = ws_checks.cell(row=summary_row, column=4, value="=COUNTIF(J2:J100, \"PASS\")")
    passed_cell.font = bold_font
    
    ws_checks.cell(row=summary_row, column=6, value="Average Error:").font = bold_font
    ws_checks.cell(row=summary_row, column=6).alignment = Alignment(horizontal="right")
    
    avg_err_cell = ws_checks.cell(row=summary_row, column=8, value="=AVERAGE(H2:H100)")
    avg_err_cell.font = bold_font
    avg_err_cell.number_format = "0.00%"
    
    for col in range(1, 11):
        ws_checks.cell(row=summary_row, column=col).border = double_bottom

    # =========================================================================
    # TAB 3: SWEEP TABLES
    # =========================================================================
    ws_sweeps = wb.create_sheet(title="Cascade Sweeps")
    ws_sweeps.views.sheetView[0].showGridLines = True
    
    # Headers
    ws_sweeps.merge_cells("A1:C1")
    sh1 = ws_sweeps["A1"]
    sh1.value = "Golden Ratio (phi) Sweep at D=13.0"
    sh1.font = header_font
    sh1.fill = header_fill
    sh1.alignment = Alignment(horizontal="center")
    
    ws_sweeps.merge_cells("E1:G1")
    sh2 = ws_sweeps["E1"]
    sh2.value = "Bulk Dimension (D) Sweep at phi=1.61803"
    sh2.font = header_font
    sh2.fill = header_fill
    sh2.alignment = Alignment(horizontal="center")
    
    sub_headers = ["Param Value", "Mean Error (%)", "Higgs Mass (GeV)"]
    for c_offset, col_start in [(0, "A"), (4, "E")]:
        for idx, sh in enumerate(sub_headers):
            cell = ws_sweeps.cell(row=2, column=c_offset + idx + 1, value=sh)
            cell.font = bold_font
            cell.fill = accent_fill
            cell.alignment = Alignment(horizontal="center")
            cell.border = thin_border
            
    # Perform mini sweep for the tables
    phi_grid = np.linspace(1.58, 1.65, 20)
    d_grid = np.linspace(12.0, 14.0, 20)
    
    print("  Running sweeps for Excel tables...")
    for idx, p in enumerate(phi_grid):
        r_row = idx + 3
        err, m_H = solve_cascade_errors(phi=p, D=13.0)
        
        c_val = ws_sweeps.cell(row=r_row, column=1, value=p)
        c_val.number_format = "0.00000"
        c_err = ws_sweeps.cell(row=r_row, column=2, value=err / 100.0)
        c_err.number_format = "0.00%"
        c_m = ws_sweeps.cell(row=r_row, column=3, value=m_H)
        c_m.number_format = "0.00"
        
        for c in range(1, 4):
            ws_sweeps.cell(row=r_row, column=c).border = thin_border
            ws_sweeps.cell(row=r_row, column=c).font = normal_font
            if idx % 2 == 1:
                ws_sweeps.cell(row=r_row, column=c).fill = zebra_fill
                
    for idx, d in enumerate(d_grid):
        r_row = idx + 3
        err, m_H = solve_cascade_errors(phi=PHI, D=d)
        
        c_val = ws_sweeps.cell(row=r_row, column=5, value=d)
        c_val.number_format = "0.00000"
        c_err = ws_sweeps.cell(row=r_row, column=6, value=err / 100.0)
        c_err.number_format = "0.00%"
        c_m = ws_sweeps.cell(row=r_row, column=7, value=m_H)
        c_m.number_format = "0.00"
        
        for c in range(5, 8):
            ws_sweeps.cell(row=r_row, column=c).border = thin_border
            ws_sweeps.cell(row=r_row, column=c).font = normal_font
            if idx % 2 == 1:
                ws_sweeps.cell(row=r_row, column=c).fill = zebra_fill

    # =========================================================================
    # Auto-adjust column widths across all sheets
    # =========================================================================
    for sheet in wb.worksheets:
        for col in sheet.columns:
            # We don't auto-size merged title block to prevent extremely wide A/E columns
            is_merged = False
            for merged_range in sheet.merged_cells.ranges:
                if col[0].column in range(merged_range.min_col, merged_range.max_col + 1) and col[0].row == 1:
                    is_merged = True
                    break
            
            max_len = 0
            for cell in col:
                if cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            col_letter = get_column_letter(col[0].column)
            # Add padding
            if is_merged and sheet.title in ["TAP Model Overview", "Cascade Sweeps"]:
                sheet.column_dimensions[col_letter].width = 25
            else:
                sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Save
    out_dir = os.path.join(os.path.dirname(src_dir), "assets")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    out_path = os.path.join(out_dir, "tap_model_comprehensive_report.xlsx")
    wb.save(out_path)
    print(f"\n  [SUCCESS] Styled Excel workbook saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
