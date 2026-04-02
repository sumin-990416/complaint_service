from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class CsoOffice(Base):
    __tablename__ = "cso_offices"

    cso_sn: Mapped[str] = mapped_column(String, primary_key=True)
    stdg_cd: Mapped[str] = mapped_column(String, nullable=False, index=True)
    cso_nm: Mapped[str] = mapped_column(String, nullable=False)
    lotno_addr: Mapped[str | None] = mapped_column(String)
    road_nm_addr: Mapped[str | None] = mapped_column(String)
    lat: Mapped[float | None] = mapped_column(Float)
    lot: Mapped[float | None] = mapped_column(Float)
    wkdy_oper_bgng_tm: Mapped[str | None] = mapped_column(String)
    wkdy_oper_end_tm: Mapped[str | None] = mapped_column(String)
    nght_oper_yn: Mapped[str | None] = mapped_column(String)
    nght_dow_expln: Mapped[str | None] = mapped_column(Text)
    wknd_oper_yn: Mapped[str | None] = mapped_column(String)
    wknd_dow_expln: Mapped[str | None] = mapped_column(Text)
    tot_crtr_ymd: Mapped[str | None] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class QueueSnapshot(Base):
    """실시간 대기 데이터 수집 이력 — 예측 모델용"""
    __tablename__ = "queue_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cso_sn: Mapped[str] = mapped_column(String, nullable=False, index=True)
    stdg_cd: Mapped[str] = mapped_column(String, nullable=False)
    task_no: Mapped[str] = mapped_column(String, nullable=False)
    task_nm: Mapped[str | None] = mapped_column(String)
    wtng_cnt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    dow: Mapped[int] = mapped_column(Integer, nullable=False)   # 0=월 … 6=일
    hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 0~23
