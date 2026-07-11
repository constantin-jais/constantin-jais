CREATE OPERATOR ?> (
  FUNCTION = public.if_then_op,
  LEFTARG = text,
  RIGHTARG = text
);
