import { X } from "lucide-react";
import { useTranslations } from "next-intl";
import ItemIcon from "./ItemIcon";

export default function ResourceAdjustmentModal({ resource, value, onChange, onClose, onApply }) {
  const t = useTranslations();
  return <div className="modal-backdrop"><section className="modal manual-adjustment-modal" role="dialog" aria-modal="true" aria-label={t("Home.manualAdjustment")}><button className="button-secondary button-icon modal-close" type="button" aria-label={t("Common.close")} onClick={onClose}><X aria-hidden="true" /></button><h2>{t("Home.manualAdjustment")}</h2><p className="adjustment-resource"><ItemIcon item={resource} />{resource.name}</p><p>{t("Home.currentAmount", { amount: resource.amount })}</p><label>{t("Home.change")}<span className="adjustment-controls"><input aria-label={`${t("Home.change")} ${resource.name}`} type="number" step="1" value={value} onChange={(event) => onChange(event.target.value)} /><button className="button-primary" type="button" onClick={onApply}>{t("Home.applyAdjustment")}</button></span></label></section></div>;
}
