from datetime import datetime

from pydantic import BaseModel, field_validator


class CsoOfficeBase(BaseModel):
    cso_sn: str
    stdg_cd: str
    cso_nm: str
    lotno_addr: str | None = None
    road_nm_addr: str | None = None
    lat: float | None = None
    lot: float | None = None
    wkdy_oper_bgng_tm: str | None = None
    wkdy_oper_end_tm: str | None = None
    nght_oper_yn: str | None = None
    nght_dow_expln: str | None = None
    wknd_oper_yn: str | None = None
    wknd_dow_expln: str | None = None
    tot_crtr_ymd: str | None = None


class CsoOfficeResponse(CsoOfficeBase):
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class RealtimeItem(BaseModel):
    cso_sn: str
    cso_nm: str
    stdg_cd: str
    task_no: str
    task_nm: str
    clot_no: str
    clot_cnter_no: str
    wtng_cnt: str
    tot_dt: str

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none_keep_str(cls, v):
        return v


class RealtimeResponse(BaseModel):
    stdg_cd: str | None = None
    total_count: int
    items: list[RealtimeItem]
