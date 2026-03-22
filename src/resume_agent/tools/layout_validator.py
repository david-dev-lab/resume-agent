"""
Playwright 渲染 HTML，感知相对 A4 单页的溢出/留白（与 utils.save_as_pdf 的 A4 语义对齐）。
"""
from __future__ import annotations

from playwright.async_api import async_playwright

from ..models import LayoutStatus

# 与 utils.save_as_pdf 中 A4 @ 96dpi 一致（297mm ≈ 1123px）
A4_HEIGHT_PX = 1123
# 整页略超：判为溢出
OVERFLOW_THRESHOLD_PX = A4_HEIGHT_PX + 28
# 模板 .page-container 上下 padding 各 10mm → 正文可用高度 ≈ 整页减此值
_PAD_VERTICAL_PX = int(round(20 / 25.4 * 96))
USABLE_CONTENT_PX = A4_HEIGHT_PX - _PAD_VERTICAL_PX
# 子块高度和低于「可排版区」该比例 → UNDERFLOW（min-height 仍会撑满白纸，故不能只看 doc 高度）
MIN_INNER_FILL_RATIO = 0.88


async def validate_html_layout(html_content: str) -> tuple[LayoutStatus, str]:
    """渲染 HTML，返回版面状态与人读反馈文案。"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            # A4 宽 @96dpi ≈ 794px，与打印换行一致
            context = await browser.new_context(
                viewport={"width": 794, "height": A4_HEIGHT_PX},
                device_scale_factor=1,
            )
            page = await context.new_page()
            await page.set_content(html_content, wait_until="domcontentloaded")

            metrics = await page.evaluate(
                """() => {
  const docH = Math.max(
    document.body ? document.body.scrollHeight : 0,
    document.documentElement ? document.documentElement.scrollHeight : 0
  );
  const pc = document.querySelector(".page-container");
  let inner = 0;
  if (pc) {
    for (const child of pc.children) {
      inner += child.offsetHeight || 0;
    }
  }
  return { docH, inner };
}"""
            )
            total_height = int(metrics["docH"])
            inner_sum = int(metrics["inner"])

        finally:
            await browser.close()

    min_inner_px = int(USABLE_CONTENT_PX * MIN_INNER_FILL_RATIO)

    if total_height > OVERFLOW_THRESHOLD_PX:
        msg = (
            f"OVERFLOW: 当前简历超过一页（渲染高度约 {total_height}px，"
            f"单页上限约 {A4_HEIGHT_PX}px）。请精简项目描述、合并技能点或缩短 summary，确保一页内。"
        )
        return LayoutStatus.OVERFLOW, msg

    if inner_sum > 0 and inner_sum < min_inner_px:
        msg = (
            f"UNDERFLOW: 正文块（.page-container 内子元素）高度约 {inner_sum}px，"
            f"低于「可排版区约 {USABLE_CONTENT_PX}px」的 {int(MIN_INNER_FILL_RATIO * 100)}%（阈值 {min_inner_px}px）；"
            "模板仍会占满一张 A4，底部易显空。请扩充项目经历/技能等（须来自用户思绪）。"
        )
        return LayoutStatus.UNDERFLOW, msg

    return LayoutStatus.PERFECT, (
        f"PERFECT: 未超页（总高约 {total_height}px）；"
        f"正文块高约 {inner_sum}px（≥{min_inner_px}px）。"
        "注意：这是像素规则，不是「肉眼铺满」；纸面留白还与字号、段距有关。"
    )
