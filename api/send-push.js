const webpush = require('web-push');
const { createClient } = require('@supabase/supabase-js');

webpush.setVapidDetails(
  `mailto:${process.env.VAPID_EMAIL}`,
  process.env.VAPID_PUBLIC_KEY,
  process.env.VAPID_PRIVATE_KEY
);

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

module.exports = async function handler(req, res) {
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // cron은 00:00 UTC = 09:00 KST로 실행됨, UTC 날짜 = KST 날짜
  const today = new Date();
  const dateStr = today.toISOString().split('T')[0];
  const year = today.getFullYear();

  // 한국 공휴일 확인
  try {
    const r = await fetch(`https://date.nager.at/api/v3/PublicHolidays/${year}/KR`);
    if (r.ok) {
      const holidays = await r.json();
      if (holidays.some(h => h.date === dateStr)) {
        return res.status(200).json({ skipped: true, reason: '공휴일' });
      }
    }
  } catch (_) {}

  const { data: subs, error } = await supabase
    .from('push_subscriptions')
    .select('subscription')
    .eq('active', true);

  if (error) return res.status(500).json({ error: error.message });
  if (!subs || !subs.length) return res.status(200).json({ sent: 0 });

  const payload = JSON.stringify({
    title: '📋 오늘의 할일',
    body: '멤버스허브에서 오늘의 업무를 확인하세요.',
    url: 'https://sfmi.members-center.co.kr'
  });

  const results = await Promise.allSettled(
    subs.map(({ subscription }) =>
      webpush.sendNotification(subscription, payload)
    )
  );

  const failed = results.filter(r => r.status === 'rejected').length;
  res.status(200).json({ total: subs.length, sent: subs.length - failed, failed });
};
