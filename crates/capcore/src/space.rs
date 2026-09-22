//! State spaces for the dynamic programme.
//!
//! A *state* is "which parts are available to build a sub-network". Two spaces:
//!
//! * [`MultisetSpace`]: a state is a sub-multiset of a universe of part classes
//!   (packed as 4-bit counts in a `u128`). Used when every part is used exactly
//!   once, or when stock is limited. Equal values share a class, so the
//!   `2^n` subsets collapse to `Π(count_i + 1)` states.
//! * [`SizeSpace`]: a state is only the number of parts, with unlimited supply of
//!   every class (E-series inventory).

use std::collections::HashMap;

pub const MAX_CLASSES: usize = 32;
pub const MAX_COUNT: u8 = 15;

pub trait Space {
    fn n_states(&self) -> usize;
    /// Number of parts in the state.
    fn size(&self, s: usize) -> usize;
    /// Classes usable as a single part (only for states of size 1).
    fn leaf_classes(&self, s: usize) -> Vec<usize>;
    /// Unordered splits into two non-empty states `(l, r)`, each reported once.
    fn for_each_split(&self, s: usize, f: &mut dyn FnMut(usize, usize));
    /// Complement of `l` inside `s` (the right side of a split).
    fn complement(&self, s: usize, l: usize) -> usize;
    /// Ordered decompositions of `s` into `m` non-empty states.
    fn for_each_composition(&self, s: usize, m: usize, f: &mut dyn FnMut(&[usize]));
}

#[derive(Debug)]
pub struct MultisetSpace {
    nclass: usize,
    states: Vec<u128>,
    sizes: Vec<usize>,
    index: HashMap<u128, usize>,
}

fn count(p: u128, i: usize) -> u8 {
    (p >> (4 * i) & 0xF) as u8
}

impl MultisetSpace {
    /// All non-empty sub-multisets of `universe` with at most `kmax` parts,
    /// sorted by size.
    pub fn new(universe: &[u8], kmax: usize) -> MultisetSpace {
        assert!(universe.len() <= MAX_CLASSES, "too many classes");
        assert!(universe.iter().all(|&c| c <= MAX_COUNT), "count too large");
        let mut states = Vec::new();
        fn rec(
            i: usize,
            uni: &[u8],
            acc: u128,
            size: usize,
            kmax: usize,
            out: &mut Vec<(usize, u128)>,
        ) {
            if i == uni.len() {
                if size > 0 {
                    out.push((size, acc));
                }
                return;
            }
            for c in 0..=uni[i] as usize {
                if size + c > kmax {
                    break;
                }
                rec(
                    i + 1,
                    uni,
                    acc | (c as u128) << (4 * i),
                    size + c,
                    kmax,
                    out,
                );
            }
        }
        rec(0, universe, 0, 0, kmax, &mut states);
        states.sort();
        let index = states
            .iter()
            .enumerate()
            .map(|(k, &(_, p))| (p, k))
            .collect();
        MultisetSpace {
            nclass: universe.len(),
            sizes: states.iter().map(|&(s, _)| s).collect(),
            states: states.into_iter().map(|(_, p)| p).collect(),
            index,
        }
    }

    pub fn id(&self, packed: u128) -> Option<usize> {
        self.index.get(&packed).copied()
    }

    pub fn packed(&self, s: usize) -> u128 {
        self.states[s]
    }

    pub fn pack(counts: &[u8]) -> u128 {
        counts
            .iter()
            .enumerate()
            .fold(0, |p, (i, &c)| p | (c as u128) << (4 * i))
    }

    /// Non-empty proper sub-multisets of `p`.
    fn for_each_sub(&self, p: u128, f: &mut dyn FnMut(u128)) {
        let digits: Vec<(usize, u8)> = (0..self.nclass)
            .map(|i| (i, count(p, i)))
            .filter(|&(_, c)| c > 0)
            .collect();
        let mut cur = vec![0u8; digits.len()];
        loop {
            let mut k = 0;
            while k < digits.len() && cur[k] == digits[k].1 {
                cur[k] = 0;
                k += 1;
            }
            if k == digits.len() {
                return;
            }
            cur[k] += 1;
            let sub = digits
                .iter()
                .zip(&cur)
                .fold(0u128, |acc, (&(i, _), &c)| acc | (c as u128) << (4 * i));
            if sub != p {
                f(sub);
            }
        }
    }
}

impl Space for MultisetSpace {
    fn n_states(&self) -> usize {
        self.states.len()
    }

    fn size(&self, s: usize) -> usize {
        self.sizes[s]
    }

    fn leaf_classes(&self, s: usize) -> Vec<usize> {
        let p = self.states[s];
        (0..self.nclass).filter(|&i| count(p, i) > 0).collect()
    }

    fn for_each_split(&self, s: usize, f: &mut dyn FnMut(usize, usize)) {
        let p = self.states[s];
        self.for_each_sub(p, &mut |l| {
            // Digit-wise l <= p, so plain subtraction never borrows across nibbles.
            let r = p - l;
            if l <= r {
                f(self.index[&l], self.index[&r]);
            }
        });
    }

    fn complement(&self, s: usize, l: usize) -> usize {
        self.index[&(self.states[s] - self.states[l])]
    }

    fn for_each_composition(&self, s: usize, m: usize, f: &mut dyn FnMut(&[usize])) {
        fn rec(
            sp: &MultisetSpace,
            rem: u128,
            m: usize,
            cur: &mut Vec<usize>,
            f: &mut dyn FnMut(&[usize]),
        ) {
            let rem_size = sp.sizes[sp.index[&rem]];
            if m == 1 {
                cur.push(sp.index[&rem]);
                f(cur);
                cur.pop();
                return;
            }
            if rem_size < m {
                return;
            }
            sp.for_each_sub(rem, &mut |l| {
                let rest = rem - l;
                if sp.sizes[sp.index[&rest]] >= m - 1 {
                    cur.push(sp.index[&l]);
                    rec(sp, rest, m - 1, cur, f);
                    cur.pop();
                }
            });
        }
        if self.sizes[s] >= m && m >= 1 {
            rec(self, self.states[s], m, &mut Vec::with_capacity(m), f);
        }
    }
}

/// States `0..kmax` stand for "networks of exactly `s + 1` parts".
#[derive(Debug)]
pub struct SizeSpace {
    pub kmax: usize,
    pub nclass: usize,
}

impl Space for SizeSpace {
    fn n_states(&self) -> usize {
        self.kmax
    }

    fn size(&self, s: usize) -> usize {
        s + 1
    }

    fn leaf_classes(&self, s: usize) -> Vec<usize> {
        if s == 0 {
            (0..self.nclass).collect()
        } else {
            Vec::new()
        }
    }

    fn for_each_split(&self, s: usize, f: &mut dyn FnMut(usize, usize)) {
        let k = s + 1;
        for i in 1..=k / 2 {
            f(i - 1, k - i - 1);
        }
    }

    fn complement(&self, s: usize, l: usize) -> usize {
        s - l - 1
    }

    fn for_each_composition(&self, s: usize, m: usize, f: &mut dyn FnMut(&[usize])) {
        fn rec(rem: usize, m: usize, cur: &mut Vec<usize>, f: &mut dyn FnMut(&[usize])) {
            if m == 1 {
                cur.push(rem - 1);
                f(cur);
                cur.pop();
                return;
            }
            for first in 1..=rem.saturating_sub(m - 1) {
                cur.push(first - 1);
                rec(rem - first, m - 1, cur, f);
                cur.pop();
            }
        }
        let k = s + 1;
        if k >= m && m >= 1 {
            rec(k, m, &mut Vec::with_capacity(m), f);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn distinct_classes_give_all_subsets() {
        let sp = MultisetSpace::new(&[1, 1, 1, 1], 4);
        assert_eq!(sp.n_states(), 15);
        let full = sp.id(MultisetSpace::pack(&[1, 1, 1, 1])).unwrap();
        let mut splits = 0;
        sp.for_each_split(full, &mut |l, r| {
            assert_eq!(sp.size(l) + sp.size(r), 4);
            assert_eq!(sp.complement(full, l), r);
            splits += 1;
        });
        // Unordered splits of a 4-set into two non-empty parts: (2^4 - 2) / 2.
        assert_eq!(splits, 7);
    }

    #[test]
    fn equal_classes_collapse() {
        let sp = MultisetSpace::new(&[5], 5);
        assert_eq!(sp.n_states(), 5);
        let full = sp.id(MultisetSpace::pack(&[5])).unwrap();
        let mut splits = Vec::new();
        sp.for_each_split(full, &mut |l, r| splits.push((sp.size(l), sp.size(r))));
        splits.sort();
        assert_eq!(splits, vec![(1, 4), (2, 3)]);
    }

    #[test]
    fn compositions_count() {
        // Ordered set partitions of a 4-set into 2 blocks: 2 * S(4,2) = 14.
        let sp = MultisetSpace::new(&[1, 1, 1, 1], 4);
        let full = sp.id(MultisetSpace::pack(&[1, 1, 1, 1])).unwrap();
        let mut n = 0;
        sp.for_each_composition(full, 2, &mut |_| n += 1);
        assert_eq!(n, 14);
        // Compositions of 5 into 3 positive parts: C(4,2) = 6.
        let ss = SizeSpace { kmax: 5, nclass: 1 };
        let mut n = 0;
        ss.for_each_composition(4, 3, &mut |p| {
            assert_eq!(p.iter().map(|&s| s + 1).sum::<usize>(), 5);
            n += 1;
        });
        assert_eq!(n, 6);
    }

    #[test]
    fn size_space_splits() {
        let ss = SizeSpace { kmax: 6, nclass: 3 };
        let mut v = Vec::new();
        ss.for_each_split(5, &mut |l, r| v.push((l + 1, r + 1)));
        assert_eq!(v, vec![(1, 5), (2, 4), (3, 3)]);
        assert_eq!(ss.leaf_classes(0), vec![0, 1, 2]);
    }
}
